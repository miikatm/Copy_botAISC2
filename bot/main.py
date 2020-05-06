import json
from pathlib import Path

import sc2

import random
import math

from sc2.ids.buff_id import BuffId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2 import position

from sc2.unit import Unit

from sc2.constants import PROBE, ZEALOT, STALKER, OBSERVER, SENTRY, ADEPT, COLOSSUS, VOIDRAY, PHOENIX, IMMORTAL, HIGHTEMPLAR, \
DARKTEMPLAR, TEMPEST, ARCHON, WARPPRISM, WARPPRISMPHASING, DISRUPTOR, DISRUPTORPHASED, MOTHERSHIP, CARRIER, ORACLE, \
    NEXUS, PYLON, GATEWAY, CYBERNETICSCORE, ASSIMILATOR, STARGATE, WARPGATE, TWILIGHTCOUNCIL, FORGE, ROBOTICSFACILITY, ROBOTICSBAY, \
    FLEETBEACON, TEMPLARARCHIVE, DARKSHRINE, PHOTONCANNON, SHIELDBATTERY , \
    SCV, DRONE, EGG, COMMANDCENTER

from sc2.constants import *

from sc2.position import *


# Bots are created as classes and they need to have on_step method defined.
# Do not change the name of the class!

class MyBot(sc2.BotAI):
    def __init__(self):

        self.actions = []
        self.last_scouted_expansion = 0  # latest scouted expansion
        self.enemy_expansions = []
        self.max_workers = 75
        # Which nexus is under attack
        self.defend_target = 0
        # Variable to determine what units to prioritize
        self.UnitTierMidAmount = 0
        self.unitTierHighAmount = 0

        self.cybercore_placement = 0

        self.our_starting_location = None

        self.locations = {'bottom_left': 0,
                          'bottom_right': 1,
                          'top_left': 2,
                          'top_right': 3,
                          'bottom': 4,
                          'top': 5,
                          'left': 6,
                          'right': 7}

        self.opponent_race = {'unknown': 0,
                              'protoss': 1,
                              'terran': 2,
                              'zerg': 3}

        self.alert = {'zergrush': 1,
                      'roach-all-in': 2,
                      'proxy': 3}

        # If enemy is rushing us, swap strategy
        self.enemy_alerts = 0
        self.enemy_alarming_building_amount = 0
        # Opponent race
        self.opponent = 0
        # Determine what the current game phase is, to determine what units to produce
        self.gamePhase = 0

        self.phase = {'Early': 0,
                      'Mid': 1,
                      'Late': 2}
        # Initial variable
        self.enemyWorker = PROBE
        # Attack group leader
        self.specialization_timer = 0
        # Gather into a ball in these locations
        self.AttackingArmyStatusList = {'Moving to Forward Rally 1': 1,
                                        'Moving to Forward Rally 2': 2,
                                        'Moving to Forward Rally 3': 3,
                                        'Commencing Attack': 4,
                                        'Under Attack': 5}
        self.AttackingArmyStatus = 0
        # Battle location if when moving to rallypoint and enemies come close
        self.BattleLocation = 0

        self.earlyBuilder = None

        self.MainArmyTarget = 0
        self.ExpansionHarassList = []
        self.ExpansionHarassTarget = 0
        #add to slow down building amounts default 165
        self.ExpansionHarassCounter = 0
        self.iterations_per_minute = 165
        # probetila
        self.workerstatus = 0
        # Armeijan tila (state)
        self.ArmyStatus = 0
        # are we atac?
        self.attacking = 0
        # Attack unit amount
        self.attackUnitAmount = 0
        # TaskForce Objective
        self.Objective = {'Adept_harass': 0,
                          'WarpPrism_strike': 1}
        self.taskForceObjective = 0
        # Special ops unit list
        self.taskForce = []
        # Target expansion for task force deep strike
        self.taskForceTarget = 0
        # Taskforce main force type
        self.taskForce_type = 0
        # Types of units in taskforce
        self.forcetype = {'disruptor': 0,
                          'gateway_units': 1}
        # Objective status
        self.taskForceSignal = 0
        # Diversion attack
        self.diversionAttack = 0
        # range at which defenders aggro
        self.def_range = 33

        self.GravitonSignal = None
        self.GravitonTarget = None

        self.ramp_points = []
        self.map_ramps = []
        self.ramp_pylon = None

        self.possible_enemy_locations = []
        self.early_expand = 0
        # Value if the game info main_base_ramp isnt really main
        self.TrueRamp = 0
        self.SecondaryRamp = 0
        self.RallyPoint = []
        self.Rallypoint_timer = 0

        self.tech = {'Robo': 1,
                     'Fleet': 2,
                     'Templar': 3,
                     'Done': 4}

        self.techPriority = 0
        self.techSecondary = 0

        self.army_weight = {PROBE: 0.5,
                            ZEALOT: 1,
                            STALKER: 2,
                            ADEPT: 2,
                            SENTRY: 1,
                            IMMORTAL: 4,
                            WARPPRISM: 2,
                            HIGHTEMPLAR: 2,
                            DARKTEMPLAR: 2,
                            COLOSSUS: 6,
                            ARCHON: 4,

                            OBSERVER: 1,
                            PHOENIX: 2,
                            VOIDRAY: 4,
                            ORACLE: 3,
                            TEMPEST: 5,
                            CARRIER: 6,
                            MOTHERSHIP: 8
                            }
        # Tier list for production line
        self.unitTierList = {
            'Low': [
                'zealot',
                'stalker',
                'sentry',
                'adept',
                'observer'
                'phoenix'],
            'Mid': [
                'immortal',
                'warpprism',
                'hightemplar',
                'darktemplar',
                'voidray',
                'oracle'],
            'High': [
                'colossus',
                'archon',
                'disruptor',
                'tempest',
                'mothership',
                'carrier']
            }
        
        self.status = {'idling': 0,
                        'attacking': 1,
                        'rallying': 2,
                        'defending': 3,
                        'harassing': 4}

        self.probestatus = {'neutral': 0,
                            'JESUSTAKETHEWHEEL': 1}

        #minkä jälkeen uusia worker scoutteja ei enään lähetetä (sekunneissa)
        self.worker_scout_end_time = 120
        self.scout = set()
        self.scout_death_cycles = 0

    with open(Path(__file__).parent / "../botinfo.json") as f:
        NAME = json.load(f)["name"]

    # On_step method is invoked each game-tick and should not take more than
    # 2 seconds to run, otherwise the bot will timeout and cannot receive new
    # orders.
    # It is important to note that on_step is asynchronous - meaning practices
    # for asynchronous programming should be followed.
    async def on_step(self, iteration):
        # Joukot kerääntyy tähän pisteeseen
        self.iteration = iteration
        self.iteration_multiplier = self.iteration / self.iterations_per_minute
        #print(iteration)

        self.actions = []
        await self.rallypoint()
        await self.army()

        if not self.possible_enemy_locations:
            for enemy_location in self.expansion_locations:
                self.possible_enemy_locations.append(enemy_location)
            self.possible_enemy_locations.sort(key= lambda x: x.distance_to(self.enemy_start_locations[0]))
        # Debug
#        if self.iteration % 60 == 0:
#            await self.chat_send(f"army size def: {self.army_size_defense} army size atk: {self.army_size_attack} status: {self.ArmyStatus}")

        if iteration == 0:
            await self.chat_send(f"It is me, {self.NAME}")
            await self.chat_send("Fear not the dark, my friend. And let the feast begin.")

        if self.time < 200:
            await self.starting_corner()
            if not self.MainArmyTarget:
                self.MainArmyTarget = self.enemy_start_locations[0]
                self.ExpansionHarassTarget = self.enemy_start_locations[0]
#            await self.custom_opening(iteration)
            if self.enemy_alerts == self.alert['zergrush'] or self.opponent == self.opponent_race['protoss']:
                await self.opening_2gate(iteration)
            elif self.enemy_alerts == self.alert['proxy']:
                await self.opening_enemy_proxy(iteration)
            elif self.enemy_alerts != self.alert['zergrush']:
                await self.opening(iteration)
        else:
            if iteration % 5 == 0:
                await self.distribute_workers()

            else:
                geysirs = self.state.vespene_geyser.closer_than(8, self.start_location)
                geysir = geysirs.closest_to(self.game_info.map_center)
                assimilator = self.units(ASSIMILATOR).ready.random
                if self.supply_left <= 4 and self.already_pending(PYLON) < 2:
                    if self.can_afford(PYLON):
                        if self.units(PYLON).ready.amount < 4:
                            await self.build(PYLON, near=self.units(NEXUS).first.position.towards(self.game_info.map_center, 5))
                        elif self.units(PYLON).ready.amount < 5:
                            await self.build(PYLON, near=geysir.position.towards(self.start_location, distance=-3))
                        else:
                            if self.iteration % 2 == 0:
                                await self.build(PYLON, near=self.units(NEXUS).ready.random.position.towards(self.game_info.map_center, 5))
                            else:
                                await self.build(PYLON, near=assimilator.position.towards(
                                    self.units(NEXUS).closest_to(assimilator), distance=-3))

                if iteration % 5 == 1:
                    await self.chrono_boost()

                if self.army_size_attack > min(50, 4.8 * self.iteration_multiplier) and not self.already_pending(NEXUS) and \
                        self.units(NEXUS).ready.amount < (min(float(10), float(self.iteration_multiplier)**0.75)):
                    await self.expand()

                elif self.units(NEXUS).ready.amount < (min(float(10), float(self.iteration_multiplier)**0.75)) and\
                    self.minerals > 1000 and not self.already_pending(NEXUS):
                    await self.expand()
                elif (self.iteration_multiplier**0.65 - self.units(NEXUS).ready.amount) > 1.7 and not self.already_pending(NEXUS):
                    await self.expand()

                else:
                    await self.upgrades_council()
                    await self.upgrades_forge()
                    await self.upgrades_cybercore()
                    await self.upgrades_robobay()
                    await self.upgrades_fleetbeacon()
                    await self.upgrades_archives()
                    await self.build_army()
                    await self.build_core_buildings()
                    await self.build_specialized_buildings()
                    await self.build_secondaryTech()

                await self.build_workers()
                if self.army_size_attack > 8:
                    await self.build_assimilator()
                if self.time > 360:
                    await self.scoutExpansions()
                await self.scoutAndHarass()
                await self.GamePhase()
                await self.TaskForce()
                # Unit Control
                await self.ArmyManager()
                await self.ArmyStatusManager()
                await self.probe_behaviour()
                await self.forwardRally()
                # Actions
                await self.do_actions(self.actions)

    async def starting_corner(self):
        if self.our_starting_location == None:
            # get x position
            if self.start_location[0] < self.game_info.map_center[0]:
                x_coord = self.locations['left']
            else:
                x_coord = self.locations['right']

            # get y position
            if self.start_location[1] < self.game_info.map_center[1]:
                y_coord = self.locations['bottom']
            else:
                y_coord = self.locations['top']

            if x_coord == self.locations['left'] and y_coord == self.locations['bottom']:
                self.our_starting_location = self.locations['bottom_left']
                #await self.chat_send(f"Starting at bottom-left")
            elif x_coord == self.locations['left'] and y_coord == self.locations['top']:
                self.our_starting_location = self.locations['top_left']
                #await self.chat_send(f"Starting at top-left")
            elif x_coord == self.locations['right'] and y_coord == self.locations['top']:
                self.our_starting_location = self.locations['top_right']
                #await self.chat_send(f"Starting at top-right")
            elif x_coord == self.locations['right'] and y_coord == self.locations['bottom']:
                self.our_starting_location = self.locations['bottom_right']
                #await self.chat_send(f"Starting at bottom-right")



    async def ramp(self, unit):
        if not self.map_ramps:
            self.map_ramps = {ramp for ramp in self.game_info.map_ramps if len(ramp.upper2_for_ramp_wall) >= 2}
        # Function from game_info i think
#        self.cached_main_base_ramp = min(ramp,
#            key=(lambda r: self.start_location.distance_to(r.top_center)),)
        for x in self.map_ramps:
            if unit.distance_to(x.top_center) < 4 and unit.distance_to(self.start_location) < 20:
                self.TrueRamp = x
            elif unit.distance_to(x.top_center) < 4 and unit.distance_to(self.start_location) < 35 and not self.SecondaryRamp:
                self.SecondaryRamp = x
            elif unit.distance_to(x.top_center) < 4 and unit.distance_to(self.enemy_start_locations[0]) < 20:
                self.enemyRamp = x


    async def rallypoint(self):
        if not self.TrueRamp and not self.RallyPoint:
            self.RallyPoint.append(self.main_base_ramp.top_center.position.towards(self.main_base_ramp.bottom_center.position, distance=-3))
        elif self.TrueRamp and self.units(NEXUS).amount < 2:
            self.RallyPoint[0] = self.TrueRamp.top_center.position.towards(self.TrueRamp.bottom_center, distance=-4)
        elif self.SecondaryRamp and self.units(NEXUS).amount > 1:
            self.RallyPoint[0] = self.SecondaryRamp.top_center.position.towards(self.units(NEXUS).first.position, distance=4)
        elif self.units(NEXUS).amount > 1:
            self.RallyPoint[0] = self.units(NEXUS).closest_to(self.RallyPoint[1]).position.towards(self.RallyPoint[1], distance=6)


    async def custom_opening(self, iteration):
        self.actions = []
        if iteration != 0 and iteration % 5 == 0:
            await self.distribute_workers()

        if len(self.taskForce) < 2:
            self.taskForce.append(self.workers.random)
        else:
            gateway_placement = self.main_base_ramp
            gateway_upper = list(gateway_placement.upper)
            gateway_upper.sort(key=lambda x: x.distance_to(self.start_location), reverse= True)
            gateway_lower = list(gateway_placement.lower)
            gateway_lower.sort(key=lambda x: x.distance_to(gateway_upper[0]))
            ramp_upper_x = gateway_placement.top_center[0]
            ramp_upper_y = gateway_placement.top_center[1]
            ramp_point_x = gateway_placement.bottom_center[0]
            ramp_point_y = gateway_placement.bottom_center[1]
            vector_length = (math.sqrt((ramp_point_x - ramp_upper_x) ** 2 + (ramp_point_y - ramp_upper_y) ** 2))
            vector_perpendicular_length = (math.sqrt((gateway_upper[1][0] - gateway_upper[0][0]) ** 2 +
                                                     (gateway_upper[1][1] - gateway_upper[0][1]) ** 2))
            perpendicular_direction_vector = (
                (gateway_upper[1][0] - gateway_upper[0][0]) / (vector_perpendicular_length / 2),
                (gateway_upper[1][1] - gateway_upper[0][1]) / (vector_perpendicular_length / 2))

            print (perpendicular_direction_vector)

            direction_vector = (
                (gateway_upper[0][0] - gateway_lower[0][0]) / (vector_length/2.25),
                (gateway_upper[0][1] - gateway_lower[0][1]) / (vector_length/2.25))

            print (direction_vector)

            gateway_placement = Point2((gateway_upper[0][0] + direction_vector[0],
                                        gateway_upper[0][1] + direction_vector[1]))

            perpendicular = Point2((gateway_upper[0][0] - perpendicular_direction_vector[0],
                                    gateway_upper[0][1] - perpendicular_direction_vector[1]))

            grand_total_placement = Point2((gateway_upper[0][0] - perpendicular_direction_vector[0] + direction_vector[0],
                                            gateway_upper[0][1] - perpendicular_direction_vector[1] + direction_vector[1]))

            print (gateway_placement)
            print (self.main_base_ramp.upper)

            self.actions.append(self.taskForce[0].move(list(self.main_base_ramp.corner_depots)[0]))
            self.actions.append(self.taskForce[1].move(list(self.main_base_ramp.corner_depots)[1]))
            #self.actions.append(self.taskForce[2].move(grand_total_placement))



        await self.do_actions(self.actions)

    async def wall_in_placements(self, ramp, gateway_offset, cybercore_offset):
        gateway_upper = list(ramp.upper)
        gateway_upper.sort(key=lambda x: x.distance_to(self.start_location), reverse=True)
        gateway_lower = list(ramp.lower)
        gateway_lower.sort(key=lambda x: x.distance_to(self.start_location), reverse=True)
        ramp_upper_x = ramp.top_center[0]
        ramp_upper_y = ramp.top_center[1]
        ramp_point_x = ramp.bottom_center[0]
        ramp_point_y = ramp.bottom_center[1]

        depot_locations = list(ramp.corner_depots)
        depot_locations.sort(key=lambda x: x.distance_to(self.start_location), reverse=True)

        vector_length = (math.sqrt((ramp_point_x - ramp_upper_x) ** 2 + (ramp_point_y - ramp_upper_y) ** 2))
        vector_perpendicular_length = (math.sqrt((gateway_upper[1][0] - gateway_upper[0][0]) ** 2 +
                                                 (gateway_upper[1][1] - gateway_upper[0][1]) ** 2))
        # Calculate yksikkö-vector
        direction_vector = (
            (gateway_upper[0][0] - gateway_lower[0][0]) / (vector_length / gateway_offset[0]),
            (gateway_upper[0][1] - gateway_lower[0][1]) / (vector_length / gateway_offset[0]))
        # Calculate perpendicular yksikkö-vector
        perpendicular_direction_vector = (
            (gateway_upper[1][0] - gateway_upper[0][0]) / (vector_perpendicular_length / gateway_offset[1]),
            (gateway_upper[1][1] - gateway_upper[0][1]) / (vector_perpendicular_length / gateway_offset[1]))
        # Gateway build location
        gateway_placement = Point2(
            (depot_locations[0][0] - perpendicular_direction_vector[0] + direction_vector[0],
             depot_locations[0][1] - perpendicular_direction_vector[1] + direction_vector[1]))

        direction_vector = (
            (gateway_upper[1][0] - gateway_lower[1][0]) / (vector_length / cybercore_offset[0]),
            (gateway_upper[1][1] - gateway_lower[1][1]) / (vector_length / cybercore_offset[0]))

        perpendicular_direction_vector = (
            (gateway_upper[1][0] - gateway_upper[0][0]) / (vector_perpendicular_length / cybercore_offset[1]),
            (gateway_upper[1][1] - gateway_upper[0][1]) / (vector_perpendicular_length / cybercore_offset[1]))
        # Cybernetics core build location
        cybercore_placement = Point2(
            (depot_locations[1][0] + perpendicular_direction_vector[0] + direction_vector[0],
             depot_locations[1][1] + perpendicular_direction_vector[1] + direction_vector[1]))

        self.cybercore_placement = cybercore_placement

        return gateway_placement


    async def opening(self, iteration):
        self.actions = []

        if iteration != 0 and iteration % 5 == 0:
            await self.distribute_workers()

        if iteration % 5 == 1:
            await self.chrono_boost()
        # Offset values for pylon and wall-in placement
        if self.our_starting_location == self.locations['bottom_left']:
            gateway_direction_offset = 1
            gateway_perpendicular_offset = -1
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = 0.25
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -7
        elif self.our_starting_location == self.locations['top_left']:
            gateway_direction_offset = -1
            gateway_perpendicular_offset = -1
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = -0.25
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -6
        elif self.our_starting_location == self.locations['top_right']:
            gateway_direction_offset = 1
            gateway_perpendicular_offset = 1
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = -1
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -5.5
        elif self.our_starting_location == self.locations['bottom_right']:
            gateway_direction_offset = -1
            gateway_perpendicular_offset = -0.5
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = -0.25
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -6

        if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY) and self.units(GATEWAY).amount < 1 and self.units(PYLON).ready.exists:
            if not self.TrueRamp:
                gateway_placement = self.main_base_ramp
            else:
                gateway_placement = self.TrueRamp

            gateway_placement = await self.wall_in_placements(gateway_placement, gateway_offset, cybercore_offset)
            await self.build(GATEWAY, gateway_placement)

        geysirs = self.state.vespene_geyser.closer_than(10, self.units(NEXUS).first.position)

        #Pylon done at 32 secs
        if not self.already_pending(PYLON) and self.units(PYLON).amount < 1:

            if not self.earlyBuilder:
                self.earlyBuilder = self.workers.furthest_to(self.units(NEXUS).first.position)

            if self.can_afford(PYLON):
                if not self.TrueRamp:
                    self.actions.append(self.earlyBuilder.build(PYLON,
                     self.main_base_ramp.top_center.towards(self.main_base_ramp.bottom_center, distance=pylon_distance)))
                else:
                    self.actions.append(self.earlyBuilder.build(PYLON,
                     self.TrueRamp.top_center.towards(self.TrueRamp.bottom_center, distance=pylon_distance)))
            elif self.time > 4:
                await self.do(self.earlyBuilder.move(self.RallyPoint[0]))
        # Build more pylons
        elif self.supply_left <= 4 and not self.already_pending(PYLON) and self.units(PYLON).amount < 2:
            if self.can_afford(PYLON):
                await self.build(PYLON, near=geysirs.random.position.towards(self.start_location, distance=-3))
        # Assimilators
        if self.units(GATEWAY).amount > 0 and self.units(ASSIMILATOR).amount < 1:
            await self.build_assimilator()
        elif self.units(CYBERNETICSCORE).exists and self.units(ASSIMILATOR).amount < 2:
            await self.build_assimilator()
        elif self.units(NEXUS).ready.amount >= 2 and self.army_size_attack > 8:
            await self.build_assimilator()
        # Train units
        for gate in self.units(GATEWAY).ready.noqueue:
            if self.enemy_race != 'Race.Zerg':
                if self.can_afford(STALKER) and self.units(CYBERNETICSCORE).ready.exists:
                    await self.do(gate.train(STALKER))
                if self.can_afford(ZEALOT) and self.units(ZEALOT).amount < 1:
                    await self.do(gate.train(ZEALOT))
            else:
                zealot_amount = 1
                if not self.enemy_alerts:
                    zealot_amount = 1
                elif self.enemy_alerts == self.alert['zergrush']:
                    zealot_amount = 1
                if self.can_afford(ADEPT) and self.units(CYBERNETICSCORE).ready.exists:
                    await self.do(gate.train(ADEPT))
                if self.can_afford(STALKER) and self.units(CYBERNETICSCORE).ready.exists and self.units(ADEPT).amount > 1:
                    await self.do(gate.train(STALKER))
                if self.can_afford(ZEALOT) and self.units(ZEALOT).amount < zealot_amount:
                    await self.do(gate.train(ZEALOT))
        # Expand
        if self.units(PYLON).ready.amount > 0 and self.units(NEXUS).amount < 2 and not self.already_pending(NEXUS):
            if self.can_afford(NEXUS):
                await self.expand_now()

        # build cybercore
        elif self.units(NEXUS).amount >= 2 and not self.units(CYBERNETICSCORE).exists and not self.already_pending(
                CYBERNETICSCORE):
            await self.build(CYBERNETICSCORE, self.cybercore_placement)
            #await self.build(CYBERNETICSCORE, near=pylon.position.towards(self.game_info.map_center, 5))
        elif self.units(CYBERNETICSCORE).ready:
            for cybercore in self.units(CYBERNETICSCORE).ready.noqueue:
                if self.can_afford(RESEARCH_WARPGATE):
                    await self.do(cybercore(RESEARCH_WARPGATE))

        if self.units(CYBERNETICSCORE).exists:
            await self.build_secondaryTech()

        if iteration % 5 != 0:
            # jottei worker rushit vie turhaan meiltä yhtä wörkeriä
            await self.scoutAndHarass()

        if self.units(PYLON).exists:
            await self.build_workers()
        await self.probe_behaviour()
        await self.GamePhase()
        await self.ArmyManager()
        await self.ArmyStatusManager()
        await self.forwardRally()
        await self.TaskForce()

        await self.do_actions(self.actions)


    async def opening_2gate(self, iteration):
        self.actions = []

        if iteration != 0 and iteration % 5 == 0:
            await self.distribute_workers()

        if iteration % 5 == 1:
            await self.chrono_boost()

        if self.our_starting_location == self.locations['bottom_left']:
            gateway_direction_offset = 1
            gateway_perpendicular_offset = -1
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = 0.25
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -7
        elif self.our_starting_location == self.locations['top_left']:
            gateway_direction_offset = -1
            gateway_perpendicular_offset = -1
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = -0.25
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -6
        elif self.our_starting_location == self.locations['top_right']:
            gateway_direction_offset = 1
            gateway_perpendicular_offset = 1
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = -1
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -5.5
        elif self.our_starting_location == self.locations['bottom_right']:
            gateway_direction_offset = -1.25
            gateway_perpendicular_offset = -1
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = -0.25
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -6

        if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY) and self.units(
                GATEWAY).amount < 1 and self.units(PYLON).ready.exists:
            if not self.TrueRamp:
                gateway_placement = self.main_base_ramp
            else:
                gateway_placement = self.TrueRamp
            gateway_placement = await self.wall_in_placements(gateway_placement, gateway_offset, cybercore_offset)
            await self.build(GATEWAY, gateway_placement)
        elif self.units(CYBERNETICSCORE).exists and self.can_afford(GATEWAY) and self.already_pending(GATEWAY) \
                and self.units(GATEWAY).amount < 2:
            await self.build(GATEWAY, near=self.units(PYLON).closest_to(self.RallyPoint[0]).position.towards(
                self.units(NEXUS).first.position))

        geysirs = self.state.vespene_geyser.closer_than(10, self.units(NEXUS).first.position)

        # Pylon done at 32 secs
        if not self.already_pending(PYLON) and self.units(PYLON).amount < 1:

            if not self.earlyBuilder:
                self.earlyBuilder = self.workers.furthest_to(self.units(NEXUS).first.position)

            if self.can_afford(PYLON):
                if not self.TrueRamp:
                    self.actions.append(self.earlyBuilder.build(PYLON,
                                                                self.main_base_ramp.top_center.towards(
                                                                    self.main_base_ramp.bottom_center,
                                                                    distance=pylon_distance)))
                else:
                    self.actions.append(self.earlyBuilder.build(PYLON,
                                                                self.TrueRamp.top_center.towards(
                                                                    self.TrueRamp.bottom_center, distance=pylon_distance)))
            elif self.time > 4:
                await self.do(self.earlyBuilder.move(self.RallyPoint[0]))

        elif self.supply_left <= 4 and not self.already_pending(PYLON) and self.units(PYLON).amount < 2:
            if self.can_afford(PYLON):
                await self.build(PYLON, near=geysirs.random.position.towards(self.start_location, distance=-3))

        if self.units(GATEWAY).amount > 0 and self.units(ASSIMILATOR).amount < 2:
            await self.build_assimilator()
        elif self.units(NEXUS).ready.amount >= 2 and self.army_size_attack > 6:
            await self.build_assimilator()

        for gate in self.units(GATEWAY).ready.noqueue:
            if self.enemy_race != 'Race.Zerg':
                if self.can_afford(ADEPT) and self.units(CYBERNETICSCORE).ready.exists:
                    await self.do(gate.train(ADEPT))
                if self.can_afford(STALKER) and self.units(CYBERNETICSCORE).ready.exists and self.units(ADEPT).amount > 1:
                    await self.do(gate.train(STALKER))
                if self.can_afford(ZEALOT) and self.units(ZEALOT).amount < 1 and self.units(ADEPT).amount > 1:
                    await self.do(gate.train(ZEALOT))
            else:
                if self.can_afford(ADEPT) and self.units(CYBERNETICSCORE).ready.exists:
                    await self.do(gate.train(ADEPT))
                if self.can_afford(STALKER) and self.units(CYBERNETICSCORE).ready.exists and self.units(ADEPT).amount > 1:
                    await self.do(gate.train(STALKER))
                if self.can_afford(ZEALOT) and self.units(ZEALOT).amount < 1 and self.units(ADEPT).amount > 1:
                    await self.do(gate.train(ZEALOT))

        if self.units(GATEWAY).amount >= 1 and not self.units(CYBERNETICSCORE).exists and not self.already_pending(CYBERNETICSCORE):
            pylon = self.units(PYLON).ready.random
            await self.build(CYBERNETICSCORE, self.cybercore_placement)
        elif self.units(CYBERNETICSCORE).amount > 0 and self.units(NEXUS).amount < 2 and not self.already_pending(NEXUS) \
                and self.known_enemy_units.closer_than(10, self.RallyPoint[0]).amount < 4:
            if self.can_afford(NEXUS):
                await self.expand_now()
        elif self.units(CYBERNETICSCORE).ready and self.units(GATEWAY).amount > 1:
            for cybercore in self.units(CYBERNETICSCORE).ready.noqueue:
                if self.can_afford(RESEARCH_WARPGATE):
                    await self.do(cybercore(RESEARCH_WARPGATE))

        if self.units(CYBERNETICSCORE).exists:
            await self.build_secondaryTech()

        if iteration % 5 != 0:
            #jottei worker rushit vie turhaan meiltä yhtä wörkeriä
            await self.scoutAndHarass()

        if self.units(PYLON).exists:
            await self.build_workers()
        await self.probe_behaviour()
        await self.GamePhase()
        await self.ArmyManager()
        await self.ArmyStatusManager()
        await self.forwardRally()
        await self.TaskForce()

        await self.do_actions(self.actions)



    async def opening_enemy_proxy(self, iteration):
        self.actions = []

        if iteration != 0 and iteration % 5 == 0:
            await self.distribute_workers()

        if iteration % 5 == 1:
            await self.chrono_boost()

        if self.our_starting_location == self.locations['bottom_left']:
            gateway_direction_offset = 1
            gateway_perpendicular_offset = -1
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = 0.25
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -7
        elif self.our_starting_location == self.locations['top_left']:
            gateway_direction_offset = -1
            gateway_perpendicular_offset = -1
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = -0.25
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -6
        elif self.our_starting_location == self.locations['top_right']:
            gateway_direction_offset = 1
            gateway_perpendicular_offset = 1
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = -1
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -5.5
        elif self.our_starting_location == self.locations['bottom_right']:
            gateway_direction_offset = -1.25
            gateway_perpendicular_offset = -1
            gateway_offset = [gateway_direction_offset, gateway_perpendicular_offset]
            cybercore_direction_offset = 1.25
            cybercore_perpendicular_offset = -0.25
            cybercore_offset = [cybercore_direction_offset, cybercore_perpendicular_offset]
            pylon_distance = -6

        if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY) and self.units(
                GATEWAY).amount < 1 and self.units(PYLON).ready.exists:
            if not self.TrueRamp:
                gateway_placement = self.main_base_ramp
            else:
                gateway_placement = self.TrueRamp
            gateway_placement = await self.wall_in_placements(gateway_placement, gateway_offset, cybercore_offset)
            await self.build(GATEWAY, gateway_placement)
        elif self.units(GATEWAY).exists and self.can_afford(GATEWAY) and self.already_pending(GATEWAY) \
                and self.units(GATEWAY).amount < 2:
            await self.build(FORGE, near=self.units(PYLON).closest_to(self.RallyPoint[0]).position.towards(
                self.units(NEXUS).first.position))
        elif self.units(FORGE).exists and self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE) \
                and self.units(CYBERNETICSCORE).amount < 1:
            await self.build(CYBERNETICSCORE, near=self.units(PYLON).ready.random)
        elif self.units(FORGE).exists and self.can_afford(GATEWAY) and self.already_pending(GATEWAY) \
                and self.units(GATEWAY).amount < 3:
            await self.build(GATEWAY, near=self.units(PYLON).closest_to(self.RallyPoint[0]).position.towards(
                self.units(NEXUS).first.position))

        if self.units(FORGE).ready.exists and self.units(PHOTONCANNON).amount < 6:
            if self.can_afford(PHOTONCANNON):
                await self.build(PHOTONCANNON, near=self.RallyPoint[0])
        if self.units(NEXUS):
            geysirs = self.state.vespene_geyser.closer_than(10, self.units(NEXUS).first.position)

        # Pylon done at 32 secs
        if not self.already_pending(PYLON) and self.units(PYLON).amount < 1:

            if not self.earlyBuilder:
                if self.units(NEXUS):
                    self.earlyBuilder = self.workers.furthest_to(self.units(NEXUS).first.position)

            if self.can_afford(PYLON):
                if not self.TrueRamp:
                    self.actions.append(self.earlyBuilder.build(PYLON,
                    self.main_base_ramp.top_center.towards(
                    self.main_base_ramp.bottom_center, distance=pylon_distance)))
                else:
                    self.actions.append(self.earlyBuilder.build(PYLON,
                    self.TrueRamp.top_center.towards(
                    self.TrueRamp.bottom_center, distance=pylon_distance)))
            elif self.time > 4:
                await self.do(self.earlyBuilder.move(self.RallyPoint[0]))

        elif self.supply_left <= 4 and not self.already_pending(PYLON) and self.units(PYLON).amount < 2:
            if self.can_afford(PYLON):
                await self.build(PYLON, near=geysirs.random.position.towards(self.start_location, distance=-3))
        elif self.supply_left <= 4 and not self.already_pending(PYLON) and self.units(PYLON).amount > 2:
            await self.build(PYLON, near=geysirs.random.position.towards(self.start_location, distance=-3))

        if self.units(GATEWAY).amount > 0 and self.units(ASSIMILATOR).amount < 2:
            await self.build_assimilator()
        elif self.units(NEXUS).ready.amount >= 2 and self.army_size_attack > 8:
            await self.build_assimilator()

        # Build Cybercore, expand
        if self.units(GATEWAY).amount >= 2 and not self.units(CYBERNETICSCORE).exists and not self.already_pending(CYBERNETICSCORE):
            pylon = self.units(PYLON).ready.random
            await self.build(CYBERNETICSCORE, self.cybercore_placement)
        elif self.units(GATEWAY).ready.amount > 0 and self.units(NEXUS).amount < 2 and not self.already_pending(NEXUS) \
                and self.known_enemy_units.closer_than(10, self.RallyPoint[0]).amount < 4 and self.army_size_attack > 15:
            if self.can_afford(NEXUS):
                await self.expand_now()
        elif self.units(CYBERNETICSCORE).ready and self.units(PHOTONCANNON).amount > 2:
            for cybercore in self.units(CYBERNETICSCORE).ready.noqueue:
                if self.can_afford(RESEARCH_WARPGATE):
                    await self.do(cybercore(RESEARCH_WARPGATE))

        for gate in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(ADEPT) and self.units(CYBERNETICSCORE).ready.exists:
                await self.do(gate.train(ADEPT))
            if self.can_afford(STALKER) and self.units(CYBERNETICSCORE).ready.exists:
                await self.do(gate.train(STALKER))

        if self.units(CYBERNETICSCORE).exists and self.army_size_attack > 20:
            await self.build_secondaryTech()


        if iteration % 5 != 0:
            #jottei worker rushit vie turhaan meiltä yhtä wörkeriä
            await self.scoutAndHarass()

        if self.units(PYLON).exists:
            await self.build_workers()
        await self.probe_behaviour()
        await self.GamePhase()
        await self.ArmyManager()
        await self.ArmyStatusManager()
        await self.forwardRally()
        await self.TaskForce()

        await self.do_actions(self.actions)

    async def expand(self):
        if self.can_afford(NEXUS):
            await self.expand_now()
            
#    async def upgrades_warpgate(self):
        #for gateway in self.units(GATEWAY).ready:
            #abilities = await self.get_available_abilities(gateway)
            #if AbilityId.MORPH_WARPGATE in abilities and self.can_afford(AbilityId.MORPH_WARPGATE):
            #    await self.do(gateway(MORPH_WARPGATE))

    async def upgrades_forge(self):
        if self.time > 300:
            for forge in self.units(FORGE).ready:
                abilities = await self.get_available_abilities(forge)
                # Ground weapons upgrade
                if self.army_size_attack > 20:
                    if AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1 in abilities:
                        if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1):
                            await self.do(forge(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1))
                    elif AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2 in abilities:
                        if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2):
                            await self.do(forge(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2))
                    elif AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3 in abilities:
                        if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3):
                            await self.do(forge(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3))
                    # Ground armor upgrade
                    if AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1 in abilities:
                        if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1):
                            await self.do(forge(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1))
                    elif AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2 in abilities:
                        if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2):
                            await self.do(forge(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2))
                    elif AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3 in abilities:
                        if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3):
                            await self.do(forge(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3))
                    # Shields upgrade
                    if AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL1 in abilities:
                        if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL1):
                            await self.do(forge(FORGERESEARCH_PROTOSSSHIELDSLEVEL1))
                    elif AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL2 in abilities:
                        if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL2):
                            await self.do(forge(FORGERESEARCH_PROTOSSSHIELDSLEVEL2))
                    elif AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL3 in abilities:
                        if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL3):
                            await self.do(forge(FORGERESEARCH_PROTOSSSHIELDSLEVEL3))

            
    async def upgrades_council(self):
        for council in self.units(TWILIGHTCOUNCIL).ready:
            abilities = await self.get_available_abilities(council)
            # blink research
            if self.units(STALKER).amount > 5:
                if AbilityId.RESEARCH_BLINK in abilities and self.can_afford(AbilityId.RESEARCH_BLINK):
                    await self.do(council(RESEARCH_BLINK))
            # Zealot Charge research
            if self.units(ZEALOT).amount > 7:
                if AbilityId.RESEARCH_CHARGE in abilities and self.can_afford(AbilityId.RESEARCH_CHARGE):
                    await self.do(council(RESEARCH_CHARGE))

            if self.units(ADEPT).amount > 7:
                if AbilityId.RESEARCH_ADEPTRESONATINGGLAIVES in abilities and self.can_afford(AbilityId.RESEARCH_ADEPTRESONATINGGLAIVES):
                    await self.do(council(RESEARCH_ADEPTRESONATINGGLAIVES))
    

    async def upgrades_cybercore(self):
        if self.techPriority == self.tech['Fleet'] or self.techPriority == self.tech['Done']:
            if self.units(FLEETBEACON).exists:
                for cybercore in self.units(CYBERNETICSCORE).ready:
                    abilities = await self.get_available_abilities(cybercore)
                    if self.army_size_attack > 20:
                        # Air Weapons Upgrade
                        if AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1 in abilities:
                            await self.do(cybercore(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1 ))
                        elif AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2 in abilities:
                            await self.do(cybercore(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2))
                        elif AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3 in abilities:
                            await self.do(cybercore(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3))
                        # Air Armor Upgrade
                        if AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1 in abilities:
                            await self.do(cybercore(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1))
                        elif AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2 in abilities:
                            await self.do(cybercore(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2))
                        elif AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3 in abilities:
                            await self.do(cybercore(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3))
                    if AbilityId.RESEARCH_WARPGATE in abilities and self.can_afford(RESEARCH_WARPGATE):
                        await self.do(cybercore(RESEARCH_WARPGATE))


    async def upgrades_robobay(self):
        for robobay in self.units(ROBOTICSBAY).ready:
            abilities = await self.get_available_abilities(robobay)
            if AbilityId.RESEARCH_EXTENDEDTHERMALLANCE in abilities:
                if self.units(COLOSSUS).amount > 1:
                    if self.can_afford(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE):
                        await self.do(robobay(RESEARCH_EXTENDEDTHERMALLANCE))

    async def upgrades_fleetbeacon(self):
        for beacon in self.units(FLEETBEACON).ready:
            abilities = await self.get_available_abilities(beacon)
            if AbilityId.RESEARCH_PHOENIXANIONPULSECRYSTALS in abilities:
                if self.units(PHOENIX).amount > 4:
                    if self.can_afford(AbilityId.RESEARCH_PHOENIXANIONPULSECRYSTALS):
                        await self.do(beacon(RESEARCH_PHOENIXANIONPULSECRYSTALS))

    async def upgrades_archives(self):
        for archives in self.units(TEMPLARARCHIVE):
            abilities = await self.get_available_abilities(archives)
            if AbilityId.RESEARCH_PSISTORM in abilities:
                    if self.can_afford(AbilityId.RESEARCH_PSISTORM):
                        await self.do(archives(RESEARCH_PSISTORM))

    async def build_workers(self):
        if self.workers.amount < 22 * self.units(NEXUS).amount and not self.already_pending(
                PROBE) and self.workers.amount < self.max_workers:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))


    async def build_core_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            # Cybernetics core
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon.position.towards(self.game_info.map_center, 5))

            # Forge
            elif (self.units(GATEWAY).ready.amount > 2 or self.units(WARPGATE).ready.amount > 2) and not self.units(FORGE) \
                    and not self.already_pending(FORGE) and self.army_size_attack > 16:
                    if self.can_afford(FORGE):
                        await self.build(FORGE, near=pylon)

            # Twilight Council
            elif self.units(CYBERNETICSCORE).ready.exists and not self.units(
                TWILIGHTCOUNCIL).exists and self.units(STALKER).amount > 8 and not self.already_pending(TWILIGHTCOUNCIL):
                    if self.can_afford(TWILIGHTCOUNCIL):
                        await self.build(TWILIGHTCOUNCIL, near=pylon)

            # Kun gateway on alle 3
            if not self.enemy_alerts:
                if (self.can_afford(GATEWAY) and not self.already_pending(GATEWAY) and
                      (self.units(WARPGATE).amount + self.units(GATEWAY).amount) < (self.iteration_multiplier**0.65) and
                      self.units(WARPGATE).amount < 3) or \
                        (not self.already_pending(GATEWAY) and self.units(WARPGATE).amount < (self.iteration_multiplier ** 0.65)
                        and self.units(WARPGATE).amount < 3 and self.minerals > 250):
                    await self.build(GATEWAY, near=self.units(PYLON).ready.closest_to(self.units(NEXUS).first).position.towards(self.game_info.map_center))
            elif self.enemy_alerts == self.alert['roach-all-in']:
                if (self.can_afford(GATEWAY) and not self.already_pending(GATEWAY) and
                      (self.units(WARPGATE).amount + self.units(GATEWAY).amount) < (self.iteration_multiplier**0.65) and
                      self.units(WARPGATE).amount < 3) and self.army_size_attack > 12 or \
                        (not self.already_pending(GATEWAY) and self.units(WARPGATE).amount < (self.iteration_multiplier ** 0.65)
                        and self.units(WARPGATE).amount < 3 and self.minerals > 400):
                    await self.build(GATEWAY, near=self.units(PYLON).ready.closest_to(self.units(NEXUS).first).position.towards(self.game_info.map_center))


            # Rakenna lisää gateway jos ei muuta, topkek
            elif self.can_afford(GATEWAY) and not self.already_pending(GATEWAY) and \
                    (self.units(WARPGATE).amount + self.units(GATEWAY).amount) < (self.iteration_multiplier**0.65) and \
                    (self.gamePhase == self.phase['Mid'] or self.gamePhase == self.phase['Late']):
                await self.build(GATEWAY, near=pylon)

            # Photon cannons
            for nexus in self.units(NEXUS).ready:
                if self.units(FORGE).ready.exists and not self.already_pending(PHOTONCANNON) and\
                self.units(NEXUS).amount > 1 and not self.units(PHOTONCANNON).closer_than(6, nexus).exists:
                    if self.can_afford(PHOTONCANNON):
                        await self.build(PHOTONCANNON, near=self.units(PYLON).ready.closest_to(nexus))

            # Shield Battery
            if self.units(NEXUS).ready.amount > 1 and self.units(SHIELDBATTERY).amount < 2 and self.units(CYBERNETICSCORE).ready.exists\
                and not self.already_pending(SHIELDBATTERY) and self.units(WARPGATE).amount > 2:
                if self.can_afford(SHIELDBATTERY):
                    await self.build(SHIELDBATTERY, near=self.units(PYLON).ready.closest_to(self.units(NEXUS).closest_to(self.RallyPoint[1])))


    async def build_specialized_buildings(self):
        if self.techPriority == self.tech['Robo'] or self.techPriority == self.tech['Done']:
            await self.robotech()

        if self.techPriority == self.tech['Fleet'] or self.techPriority == self.tech['Done']:
            await self.fleettech()

        if self.techPriority == self.tech['Templar'] or self.techPriority == self.tech['Done']:
            await self.templartech()


    async def robotech(self):
        pylon = self.units(PYLON).ready.random
        if self.units(CYBERNETICSCORE).ready.amount > 0 and self.units(ROBOTICSFACILITY).ready.amount < (
                self.iteration_multiplier ** 0.25) and not \
                self.already_pending(ROBOTICSFACILITY) and self.army_size_attack > 14:
            if self.can_afford(ROBOTICSFACILITY):
                await self.build(ROBOTICSFACILITY, near=pylon)

        elif self.units(ROBOTICSFACILITY).ready.amount > 0 and not self.units(
                ROBOTICSBAY).exists and not self.already_pending(ROBOTICSBAY):
            if self.can_afford(ROBOTICSBAY):
                await self.build(ROBOTICSBAY, near=pylon)

        if self.units(ROBOTICSFACILITY).ready.amount > 1 and self.units(ROBOTICSBAY).exists:
            if not self.specialization_timer:
                self.specialization_timer = self.time
            elif self.time - self.specialization_timer > 180:
                self.techPriority = self.tech['Done']


    async def fleettech(self):
        pylon = self.units(PYLON).ready.random
        # Stargate
        if self.units(STARGATE).ready.amount < (self.iteration_multiplier ** 0.25) and \
                not self.already_pending(STARGATE) and self.army_size_attack > 14:
            if self.can_afford(STARGATE):
                await self.build(STARGATE, near=pylon)

        # Fleet Beacon
        elif self.units(STARGATE).ready.amount > 0 and self.units(
                FLEETBEACON).ready.amount < 1 and not self.already_pending(FLEETBEACON):
            if self.can_afford(FLEETBEACON):
                await self.build(FLEETBEACON, near=pylon)

        if self.units(STARGATE).ready.amount > 1 and self.units(FLEETBEACON).exists:
            if not self.specialization_timer:
                self.specialization_timer = self.time
            elif self.time - self.specialization_timer > 180:
                self.techPriority = self.tech['Done']


    async def templartech(self):
        pylon = self.units(PYLON).ready.random
        # Twilight Council
        if not self.units(TWILIGHTCOUNCIL).exists and not self.already_pending(TWILIGHTCOUNCIL) and \
            self.units(CYBERNETICSCORE).ready.exists and self.army_size_attack > 14:
                if self.can_afford(TWILIGHTCOUNCIL):
                    await self.build(TWILIGHTCOUNCIL, near=pylon)

        # Templar Archives
        elif self.units(TWILIGHTCOUNCIL).ready.amount > 0 and self.units(
            TEMPLARARCHIVE).ready.amount < 1 and not self.already_pending(TEMPLARARCHIVE):
            if self.can_afford(TEMPLARARCHIVE):
                await self.build(TEMPLARARCHIVE, near=pylon)

        # Dark Shrine
        elif self.units(TWILIGHTCOUNCIL).ready.amount > 0 and self.units(
            DARKSHRINE).ready.amount < 1 and not self.already_pending(DARKSHRINE):
            if self.can_afford(DARKSHRINE):
                await self.build(DARKSHRINE, near=pylon)

        if self.units(TEMPLARARCHIVE).exists and self.units(DARKSHRINE).exists:
            if not self.specialization_timer:
                self.specialization_timer = self.time
            elif self.time - self.specialization_timer > 180:
                self.techPriority = self.tech['Done']


    async def build_secondaryTech(self):
        pylon = self.units(PYLON).ready.closest_to(self.units(NEXUS).first.position)
        if self.techSecondary == self.tech['Robo']:
            if self.units(CYBERNETICSCORE).ready.exists and self.units(ROBOTICSFACILITY).ready.amount < 1 and not \
                    self.already_pending(ROBOTICSFACILITY):
                if self.can_afford(ROBOTICSFACILITY):
                    await self.build(ROBOTICSFACILITY, near=pylon.position.towards(self.RallyPoint[0]))

        elif self.techSecondary == self.tech['Fleet']:
            if self.units(CYBERNETICSCORE).ready.exists and self.units(STARGATE).ready.amount < 1 \
            and not self.already_pending(STARGATE):
                if self.can_afford(STARGATE):
                    await self.build(STARGATE, near=pylon.position.towards(self.RallyPoint[0]))

        elif self.techSecondary == self.tech['Templar']:
            if self.units(CYBERNETICSCORE).ready.exists and not self.units(
                TWILIGHTCOUNCIL).exists and not self.already_pending(TWILIGHTCOUNCIL):
                    if self.can_afford(TWILIGHTCOUNCIL):
                        await self.build(TWILIGHTCOUNCIL, near=pylon.position.towards(self.RallyPoint[0]))

            # Templar Archives
            if self.units(TWILIGHTCOUNCIL).ready.amount > 0 and self.units(
                TEMPLARARCHIVE).ready.amount < 1 and not self.already_pending(TEMPLARARCHIVE):
                if self.can_afford(TEMPLARARCHIVE):
                    await self.build(TEMPLARARCHIVE, near=pylon.position.towards(self.RallyPoint[0]))


    async def build_assimilator(self):
        for nexus in self.units(NEXUS).ready:
            geysirs = self.state.vespene_geyser.closer_than(10, nexus)
            for vaspene in geysirs:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists and \
                        (self.units(GATEWAY).exists or self.units(WARPGATE).exists):
                    await self.do(worker.build(ASSIMILATOR, vaspene))


    async def chrono_boost(self):
        priorityList = ['roboticsfacility', 'stargate']
        if self.units(NEXUS).amount > 0:
            for nexus in self.units(NEXUS):
                boost = await self.get_available_abilities(nexus)
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in boost:
                    building = self.units.structure.exclude_type(NEXUS).filter(lambda x: x.noqueue == False)
                    if self.time < 300:
                        building = building.filter(lambda x: x.name.lower() in priorityList)
                        if len(building) > 0:
                            await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, building.first))
                    else:
                        if len(building) > 0:
                            await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, building.first))


    async def GamePhase(self):
        if self.gamePhase == self.phase['Early'] and (self.units(ROBOTICSFACILITY).exists or self.units(STARGATE).exists
            or self.units(TWILIGHTCOUNCIL).exists):
            self.gamePhase = self.phase['Mid']
        elif self.units(ROBOTICSBAY).exists and self.units(FLEETBEACON).exists and self.units(TEMPLARARCHIVE).exists and\
                self.units(DARKSHRINE).exists:
            self.gamePhase = self.phase['Late']


    async def build_army(self):
        # for key, value in sorted(self.army_weigth.iteritems(), key=lambda (k, v): (v, k)):: what dis?
        for stargate in self.units(STARGATE).ready.noqueue:
            if self.gamePhase == self.phase['Mid'] and self.army_size_attack > 6:
                if self.units(FLEETBEACON).exists:
                    if self.can_afford(TEMPEST) and self.supply_left > 0 \
                            and self.units(TEMPEST).amount < self.max_tempest and self.units(FLEETBEACON).ready.exists:
                        await self.do(stargate.train(TEMPEST))

                if self.can_afford(VOIDRAY) and self.supply_left > 0 and self.units(VOIDRAY).amount < self.max_voidray:
                    await self.do(stargate.train(VOIDRAY))

                if self.can_afford(PHOENIX) and self.supply_left > 0 and self.units(PHOENIX).amount < self.max_phoenix:
                    await self.do(stargate.train(PHOENIX))

            if self.gamePhase == self.phase['Late']:
                if self.can_afford(VOIDRAY) and self.supply_left > 0 and self.units(VOIDRAY).amount < self.max_voidray and\
                    self.units(VOIDRAY).amount/2 < self.units(TEMPEST).amount:
                    await self.do(stargate.train(VOIDRAY))
                elif self.can_afford(TEMPEST) and self.supply_left > 0 and self.units(TEMPEST).amount < self.max_tempest and\
                    self.units(VOIDRAY).amount/2 > self.units(TEMPEST).amount and self.units(FLEETBEACON).ready.exists:
                    await self.do(stargate.train(TEMPEST))

                if self.can_afford(PHOENIX) and self.supply_left > 0 and self.units(PHOENIX).amount < self.max_phoenix:
                    await self.do(stargate.train(PHOENIX))

        for robofacility in self.units(ROBOTICSFACILITY).ready.noqueue:
            if self.gamePhase == self.phase['Mid'] or self.gamePhase == self.phase['Late'] and self.army_size_attack > 4:
                if self.units(ROBOTICSBAY).ready.exists:
                    if self.can_afford(COLOSSUS) and self.supply_left > 0 and self.units(COLOSSUS).amount < self.max_colossus:
                        await self.do(robofacility.train(COLOSSUS))

                    if self.can_afford(DISRUPTOR) and self.supply_left > 0 and self.units(
                           DISRUPTOR).amount < self.max_disruptor:
                        await self.do(robofacility.train(DISRUPTOR))

                if (self.UnitTierHighAmount >= 2 and self.units(ROBOTICSBAY).ready) or not self.units(ROBOTICSBAY).exists:
                    if self.can_afford(IMMORTAL) and self.supply_left > 0 and self.units(
                        IMMORTAL).amount < self.max_immortal:
                        await self.do(robofacility.train(IMMORTAL))

                    if self.can_afford(WARPPRISM) and self.supply_left > 0 and self.units(
                        WARPPRISM).amount < self.max_warpprism and self.army_size_attack > 15:
                        await self.do(robofacility.train(WARPPRISM))

            if self.can_afford(OBSERVER) and self.supply_left > 0 and self.units(OBSERVER).amount < self.max_observer and\
                self.army_size_attack > 12:
                await self.do(robofacility.train(OBSERVER))

        for gate in self.units(GATEWAY).ready.noqueue:
            if (self.gamePhase == self.phase['Mid'] and self.UnitTierMidAmount < 4) or\
                    (self.GamePhase == self.phase['Late'] and self.UnitTierMidAmount < 4 and self.UnitTierHighAmount < 3):
                if self.units(TEMPLARARCHIVE).ready.exists:
                    if self.can_afford(HIGHTEMPLAR) and self.supply_left > 0 and self.units(HIGHTEMPLAR).amount < self.max_hightemplar:
                        await self.do(gate.train(HIGHTEMPLAR))

                if self.units(DARKSHRINE).ready.exists:
                    if self.can_afford(DARKTEMPLAR) and self.supply_left > 0 and self.units(DARKTEMPLAR).amount < self.max_darktemplar:
                        await self.do(gate.train(DARKTEMPLAR))

            else:
                if self.units(CYBERNETICSCORE).ready:
                    if self.can_afford(ADEPT) and self.supply_left > 0 and self.units(ADEPT).amount < self.max_adept:
                        await self.do(gate.train(ADEPT))

                if self.units(CYBERNETICSCORE).ready:
                    if self.can_afford(STALKER) and self.supply_left > 0 and self.units(STALKER).amount < self.max_stalker:
                        await self.do(gate.train(STALKER))

                if self.can_afford(ZEALOT) and self.supply_left > 0 and self.units(ZEALOT).amount < self.max_zealot:
                    await self.do(gate.train(ZEALOT))

                if self.units(CYBERNETICSCORE).ready:
                    if self.can_afford(SENTRY) and self.supply_left > 0 and self.units(SENTRY).amount < self.max_sentry:
                        await self.do(gate.train(SENTRY))

                if self.units(TEMPLARARCHIVE).ready.exists:
                    if self.can_afford(HIGHTEMPLAR) and self.supply_left > 0 and self.units(HIGHTEMPLAR).amount < self.max_hightemplar:
                        await self.do(gate.train(HIGHTEMPLAR))

                if self.units(DARKSHRINE).ready.exists:
                    if self.can_afford(DARKTEMPLAR) and self.supply_left > 0 and self.units(DARKTEMPLAR).amount < self.max_darktemplar:
                        await self.do(gate.train(DARKTEMPLAR))

            if self.minerals > 400 or self.time < 300:

                if self.can_afford(ZEALOT) and self.supply_left > 0 and self.units(ZEALOT).amount < self.max_zealot:
                    await self.do(gate.train(ZEALOT))

                if self.vespene > 400 or self.time < 300:
                    if self.units(CYBERNETICSCORE).ready:
                        if self.can_afford(ADEPT) and self.supply_left > 0 and self.units(
                                ADEPT).amount < self.max_adept:
                            await self.do(gate.train(ADEPT))

                    if self.can_afford(STALKER) and self.supply_left > 0 and self.units(
                            STALKER).amount < self.max_stalker:
                        await self.do(gate.train(STALKER))

        for warpgate in self.units(WARPGATE).ready:
            abilities = await self.get_available_abilities(warpgate)
            # Warp location
            if self.ArmyStatus != self.status['attacking']:
                warp_pos = self.units(PYLON).closest_to(self.RallyPoint[0]).position.to2.random_on_distance(4)
            else:
                if self.units(WARPPRISMPHASING).exists:
                    warp_pos = self.units(WARPPRISMPHASING).closest_to(
                        self.enemy_start_locations[0]).position.to2.random_on_distance(4)
                else:
                    warp_pos = self.units(PYLON).closest_to(
                        self.enemy_start_locations[0]).position.to2.random_on_distance(4)

            if (self.gamePhase == self.phase['Mid'] and self.UnitTierMidAmount < 4) or \
                (self.GamePhase == self.phase['Late'] and self.UnitTierMidAmount < 4 and self.UnitTierHighAmount < 3):

                if self.units(TEMPLARARCHIVE).ready.exists and AbilityId.WARPGATETRAIN_HIGHTEMPLAR in abilities:
                    if self.can_afford(HIGHTEMPLAR) and self.supply_left > 0 and self.units(HIGHTEMPLAR).amount < self.max_hightemplar:
                        placement = await self.find_placement(AbilityId.WARPGATETRAIN_HIGHTEMPLAR, warp_pos,
                                                              placement_step=1)
                        if placement is None:
                            # return ActionResult.CantFindPlacementLocation
                            return
                        self.actions.append(warpgate.warp_in(HIGHTEMPLAR, placement))

                if self.units(DARKSHRINE).ready.exists and AbilityId.WARPGATETRAIN_DARKTEMPLAR in abilities:
                    if self.can_afford(DARKTEMPLAR) and self.supply_left > 0 and self.units(DARKTEMPLAR).amount < self.max_darktemplar:
                            placement = await self.find_placement(AbilityId.WARPGATETRAIN_DARKTEMPLAR, warp_pos,
                                                                  placement_step=1)
                            if placement is None:
                                # return ActionResult.CantFindPlacementLocation
                                return
                            self.actions.append(warpgate.warp_in(DARKTEMPLAR, placement))
            else:
                if AbilityId.WARPGATETRAIN_ZEALOT in abilities:
                    if self.can_afford(ADEPT) and self.supply_left > 0 and self.units(ADEPT).amount < self.max_adept:
                        placement = await self.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, warp_pos,
                                                              placement_step=1)
                        if placement is None:
                            # return ActionResult.CantFindPlacementLocation
                            return
                        self.actions.append(warpgate.warp_in(ADEPT, placement))

                if AbilityId.WARPGATETRAIN_SENTRY in abilities:
                    if self.can_afford(SENTRY) and self.supply_left > 0 and self.units(SENTRY).amount < self.max_sentry:
                        placement = await self.find_placement(AbilityId.WARPGATETRAIN_SENTRY, warp_pos,
                                                              placement_step=1)
                        if placement is None:
                            # return ActionResult.CantFindPlacementLocation
                            return
                        self.actions.append(warpgate.warp_in(SENTRY, placement))

                if AbilityId.WARPGATETRAIN_STALKER in abilities:
                    if self.can_afford(STALKER) and self.supply_left > 0 and self.units(STALKER).amount < self.max_stalker:
                        placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, warp_pos,
                                                              placement_step=1)
                        if placement is None:
                            # return ActionResult.CantFindPlacementLocation
                            return
                        self.actions.append(warpgate.warp_in(STALKER, placement))

                if AbilityId.WARPGATETRAIN_ZEALOT in abilities:
                    if self.can_afford(ZEALOT) and self.supply_left > 0 and self.units(ZEALOT).amount < self.max_zealot:
                        placement = await self.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, warp_pos,
                                                              placement_step=1)
                        if placement is None:
                            # return ActionResult.CantFindPlacementLocation
                            return
                        self.actions.append(warpgate.warp_in(ZEALOT, placement))

                if self.units(TEMPLARARCHIVE).ready.exists and AbilityId.WARPGATETRAIN_HIGHTEMPLAR in abilities:
                    if self.can_afford(HIGHTEMPLAR) and self.supply_left > 0 and self.units(HIGHTEMPLAR).amount < self.max_hightemplar:
                        placement = await self.find_placement(AbilityId.WARPGATETRAIN_HIGHTEMPLAR, warp_pos,
                                                              placement_step=1)
                        if placement is None:
                            # return ActionResult.CantFindPlacementLocation
                            return
                        self.actions.append(warpgate.warp_in(HIGHTEMPLAR, placement))

                if self.units(DARKSHRINE).ready.exists and AbilityId.WARPGATETRAIN_DARKTEMPLAR in abilities:
                    if self.can_afford(DARKTEMPLAR) and self.supply_left > 0 and self.units(DARKTEMPLAR).amount < self.max_darktemplar:
                            placement = await self.find_placement(AbilityId.WARPGATETRAIN_DARKTEMPLAR, warp_pos,
                                                                  placement_step=1)
                            if placement is None:
                                # return ActionResult.CantFindPlacementLocation
                                return
                            self.actions.append(warpgate.warp_in(DARKTEMPLAR, placement))

            if self.minerals > 400 or self.time < 300:

                if AbilityId.WARPGATETRAIN_ZEALOT in abilities:
                    if self.can_afford(ADEPT) and self.supply_left > 0 and self.units(ADEPT).amount < self.max_adept:
                        placement = await self.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, warp_pos,
                                                              placement_step=1)
                        if placement is None:
                            # return ActionResult.CantFindPlacementLocation
                            return
                        self.actions.append(warpgate.warp_in(ADEPT, placement))

                if AbilityId.WARPGATETRAIN_ZEALOT in abilities:
                    if self.can_afford(ZEALOT) and self.supply_left > 0 and self.units(ZEALOT).amount < self.max_zealot:
                        placement = await self.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, warp_pos,
                                                              placement_step=1)
                        if placement is None:
                            # return ActionResult.CantFindPlacementLocation
                            return
                        self.actions.append(warpgate.warp_in(ZEALOT, placement))

                if self.vespene > 400:
                    if AbilityId.WARPGATETRAIN_STALKER in abilities:
                        if self.can_afford(STALKER) and self.supply_left > 0 and self.units(
                                STALKER).amount < self.max_stalker:
                            placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, warp_pos,
                                                                  placement_step=1)
                            if placement is None:
                                # return ActionResult.CantFindPlacementLocation
                                return
                            self.actions.append(warpgate.warp_in(STALKER, placement))



    def find_GroundTarget(self, attacker):
        #Jos jotain muuta ku rakennuksia, prioo ne
        if self.diversionAttack == 1:
            vihut = self.known_enemy_units.not_flying.exclude_type(UnitTypeId.EGG).closer_than(10, attacker)
            if vihut.not_structure.exclude_type( self.enemyWorker).closer_than(20, attacker).exists:
                return vihut.not_structure.exclude_type(self.enemyWorker).closest_to(attacker)
            elif vihut.filter(lambda u: u.can_attack_ground).exists:
                return vihut.filter(lambda u: u.can_attack_ground).closest_to(attacker)
            elif vihut.exists:
                return vihut.closest_to(attacker)
            else:
                return self.MainArmyTarget
        else:
            vihut = self.known_enemy_units.not_flying.exclude_type(UnitTypeId.EGG)
            if vihut.not_structure.exclude_type(self.enemyWorker).closer_than(20, attacker).exists:
                return vihut.not_structure.exclude_type(self.enemyWorker).closest_to(attacker)
            elif vihut.filter(lambda u: u.can_attack_ground).exists:
                return vihut.filter(lambda u: u.can_attack_ground).closest_to(attacker)
            elif vihut.exists:
                return vihut.closest_to(attacker)
            else:
                return self.MainArmyTarget

    def find_HarassTarget(self, attacker):
        vihut = self.known_enemy_units.not_flying.exclude_type(UnitTypeId.EGG)
        #Harass toimii vaan ei structeihin
        if vihut.not_structure.exists:
            return vihut.not_structure.closest_to(attacker)
        else:
            return self.MainArmyTarget

    def find_AirTarget(self, attacker):
        vihut = self.known_enemy_units.exclude_type(UnitTypeId.EGG)
        if vihut.flying.not_structure.closer_than(20, attacker).exists \
            or vihut.filter(lambda x: x.name.lower() == 'colossus').closer_than(20, attacker).exists:
            return vihut.flying.not_structure.closest_to(attacker)
        elif vihut.flying.closer_than(20, attacker).exists:
            return vihut.flying.exclude_type(UnitTypeId.EGG).closest_to(attacker)
        else:
            return self.MainArmyTarget

    def find_AnyTarget(self, attacker):
        vihut = self.known_enemy_units.exclude_type(UnitTypeId.EGG)
        if vihut.not_structure.exclude_type(self.enemyWorker).closer_than(20, attacker).exists:
            return vihut.not_structure.exclude_type(self.enemyWorker).closest_to(attacker)
        elif vihut.filter(lambda u: u.can_attack_ground).closer_than(20, attacker).exists:
            return vihut.filter(lambda u: u.can_attack_ground).closest_to(attacker)
        elif vihut.closer_than(20, attacker).exists:
            return vihut.exclude_type(UnitTypeId.EGG).closest_to(attacker)
        else:
            return self.MainArmyTarget


    def find_AnyTarget_AirPriority(self, attacker):
        vihut = self.known_enemy_units.exclude_type(UnitTypeId.EGG)
        if vihut.not_structure.flying.closer_than(20, attacker).exists:
            return vihut.not_structure.flying.closest_to(attacker)
        elif vihut.not_structure.closer_than(20, attacker).exists:
            return vihut.not_structure.closest_to(attacker)
        elif vihut.closer_than(20, attacker).exists:
            return vihut.closest_to(attacker)
        else:
            return self.MainArmyTarget

    def find_ExpansionTargets(self, attacker):
        self.HarassArmyExpansions(attacker)



    async def scoutSetForwardRallyLocation(self, unit):
        if unit.distance_to(self.units(NEXUS).first.position) > 52 and unit.distance_to(self.units(NEXUS).first.position) < 54 \
            and len(self.RallyPoint) == 1:
                self.RallyPoint.append(unit.position)

        elif unit.distance_to(self.units(NEXUS).first.position) > 72 and unit.distance_to(self.units(NEXUS).first.position) < 74 \
            and len(self.RallyPoint) == 2:
                self.RallyPoint.append(unit.position)

        elif unit.distance_to(self.enemy_start_locations[0]) > 44 and unit.distance_to(self.enemy_start_locations[0]) < 46 \
            and len(self.RallyPoint) == 3:
            self.RallyPoint.append(unit.position)


    async def scoutAndHarass(self):
        #lähetä lähin probe scouttaamaan ja/tai kiusaamaan. Tätähän ei kannata tehdä kuin kerran, jos ollaan rehellisiä?
        #ei scouttaa, jos alle 10 probea hengissä
        #jos probet on rip, ei  kaada peliä (vaikka se ollaan jo hävitty...)
        if self.workers.exists and self.workers.find_by_tag(self.scout) == None and self.time < self.worker_scout_end_time and self.workers.amount > 9:
            self.scout = self.workers.closest_to(self.units(NEXUS).first.position).tag
        if self.workers.find_by_tag(self.scout) is not None:
            scoutP = self.workers.find_by_tag(self.scout)
            await self.ramp(scoutP)
            await self.scoutSetForwardRallyLocation(scoutP)
                   #lainattu teranin reapereista: onko vihuja 10 sisällä?
            threatClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground).closer_than(10, scoutP)
            if threatClose.exists:
                #Jos kilvet laskeneet alhaalla ja vihuja lähellä --> kikeen, vaikkapa kohti omaa basea
                if scoutP.shield_percentage < 0.9:
                    await self.scoutExpansions()
                #jos kohteita lähellä, hyökkää lähimpään
                elif self.known_enemy_structures.amount < 2:
                    self.actions.append(scoutP.move(self.enemy_start_locations[0]))
                else:
                    self.actions.append(scoutP.attack(self.find_HarassTarget(scoutP)))
            #jos ketään ei näy, siirry kohti vastustajan aloituspistettä
            else:
                self.actions.append(scoutP.attack(self.find_HarassTarget(scoutP)))

        if self.opponent == self.opponent_race['unknown']:
            for enemy_unit in self.known_enemy_units:
                if enemy_unit.name.lower() == "probe":
                    self.opponent = self.opponent_race['protoss']
                    self.enemyWorker = PROBE
                elif enemy_unit.name.lower() == "scv":
                    self.opponent = self.opponent_race['terran']
                    self.enemyWorker = SCV
                elif enemy_unit.name.lower() == "drone":
                    self.opponent = self.opponent_race['zerg']
                    self.enemyWorker = DRONE
        if self.time < 150:
            enemy_structures = self.known_enemy_structures

            if enemy_structures.exists:
                self.enemy_alarming_building_amount = 0
                for structure in enemy_structures:
                    if structure.name.lower() == 'spawningpool':
                        self.enemy_alarming_building_amount = self.enemy_alarming_building_amount + 1
                        if self.enemy_alarming_building_amount >= 2:
                            self.enemy_alerts = self.alert['zergrush']
                    elif structure.name.lower() == 'roachwarren':
                        self.enemy_alerts = self.alert['roach-all-in']
                    elif structure.name.lower() == 'barracks' and structure.distance_to(self.enemy_start_locations[0]) < 20:
                        self.enemy_alarming_building_amount = self.enemy_alarming_building_amount + 1
                        if self.enemy_alarming_building_amount > 3:
                            self.enemy_alerts = self.alert['zergrush']

            if self.known_enemy_structures.closer_than(100, self.units(NEXUS).first.position).exists:
                self.enemy_alerts = self.alert['proxy']
            if self.workers.find_by_tag(self.scout) is not None:
                scoutP = self.workers.find_by_tag(self.scout)
                if scoutP.distance_to(self.enemy_start_locations[0]) < 7 and self.opponent == self.opponent_race['terran'] and self.time > 50:
                    save_me = [x for x in enemy_structures if x.name.lower() == 'barracks']
                    if not save_me:
                        self.enemy_alerts = self.alert['proxy']



    async def scoutExpansions(self):
        if self.units.find_by_tag(self.scout) == None:
            # Prioritize observers for scouting
            if self.units(OBSERVER).exists:
                self.scout = self.units(OBSERVER).closest_to(self.units(NEXUS).first.position).tag
                self.scout_death_cycles = self.scout_death_cycles + 1
            elif self.workers.exists and self.time > 300 and self.workers.amount > 9:
                self.scout_death_cycles = self.scout_death_cycles + 1
                self.scout = self.workers.closest_to(self.units(NEXUS).first.position).tag
                self.scout_death_cycles = self.scout_death_cycles + 1
                # Skip expansion, if we die too many times
            if self.scout_death_cycles > 2:
                if len(self.possible_enemy_locations) > (self.last_scouted_expansion + 1):
                    self.last_scouted_expansion = self.last_scouted_expansion + 1
                    self.scout_death_cycles = 0
                else:
                    self.last_scouted_expansion = 0
                    self.scout_death_cycles = 0

        elif self.units.find_by_tag(self.scout) is not None:
            scoutP = self.units.find_by_tag(self.scout)
            threatClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground).closer_than(10, scoutP)
            if threatClose.exists:
                #Jos kilvet laskeneet alhaalla ja vihuja lähellä --> kikeen, vaikkapa kohti omaa basea
                if scoutP.shield_percentage < 0.9:
                    self.actions.append(scoutP.move(self.RallyPoint[0]))
            else:
                self.actions.append(scoutP.move(self.possible_enemy_locations[self.last_scouted_expansion]))
            # if enemies have expanded to expa, move to next expansion location
            if self.known_enemy_structures.closer_than(8, self.possible_enemy_locations[self.last_scouted_expansion]):
                if len(self.possible_enemy_locations) > (self.last_scouted_expansion + 1):
                    if self.possible_enemy_locations[self.last_scouted_expansion] not in self.enemy_expansions:
                        self.enemy_expansions.append(self.possible_enemy_locations[self.last_scouted_expansion])
                    self.last_scouted_expansion = self.last_scouted_expansion + 1
                else:
                    self.last_scouted_expansion = 0
            elif scoutP.distance_to(self.possible_enemy_locations[self.last_scouted_expansion]) < 4 and \
                    not self.known_enemy_structures.closer_than(8, self.possible_enemy_locations[self.last_scouted_expansion]) or \
                self.units(NEXUS).closer_than(8, self.possible_enemy_locations[self.last_scouted_expansion]):
                if len(self.possible_enemy_locations) > (self.last_scouted_expansion + 1):
                    self.last_scouted_expansion = self.last_scouted_expansion + 1
                else:
                    self.last_scouted_expansion = 0


    async def HarassArmyExpansions(self, attacker):
        if self.time > 300:
            vihut = self.known_enemy_units.exclude_type(UnitTypeId.EGG)

            if len(self.ExpansionHarassList) < 2 and len(self.possible_enemy_locations) > 4:
                self.ExpansionHarassList = [Point2(x) for x in self.possible_enemy_locations if x.distance_to(self.enemy_start_locations[0]) > 40]
            #self.ExpansionHarassTarget = self.possible_enemy_locations
            if self.enemy_start_locations[0] in self.ExpansionHarassList:
                self.possible_enemy_locations.pop()
                self.possible_enemy_locations.pop()

            if len(self.ExpansionHarassList) >= 1:
                if self.known_enemy_structures.closer_than(8, self.ExpansionHarassList[self.ExpansionHarassCounter]) \
                        and attacker.distance_to(self.ExpansionHarassList[self.ExpansionHarassCounter]) < 7:
                    if vihut.not_structure.closer_than(9, attacker).filter(
                            lambda x: x.name.lower() == self.enemyWorker.lower).exists:
                        self.actions.append(attacker.attack(vihut.not_structure.filter(lambda x: x.name.lower() == self.enemyWorker.lower).closest_to(
                            attacker)))
                    elif self.known_enemy_structures.exists:
                        self.actions.append(attacker.attack(self.known_enemy_structures.closest_to(attacker)))

                elif not self.known_enemy_structures.closer_than(8, self.ExpansionHarassList[self.ExpansionHarassCounter]) \
                        and attacker.distance_to(self.ExpansionHarassList[self.ExpansionHarassCounter]) < 7:
                    if len(self.ExpansionHarassList) > self.ExpansionHarassCounter + 1:
                        self.ExpansionHarassCounter = self.ExpansionHarassCounter + 1
                    else:
                        self.ExpansionHarassCounter = 0
                    self.actions.append(attacker.move(self.ExpansionHarassTarget))
                else:
                    self.actions.append(attacker.move(self.ExpansionHarassTarget))
            else:
                self.ArmyStatus = self.status['rallying']

            self.ExpansionHarassTarget = self.ExpansionHarassList[self.ExpansionHarassCounter]




    async def army(self):

        self.max_army_supply = 200
        army_supply = (self.supply_cap - self.workers.amount)
        if self.opponent == self.opponent_race['unknown']:
            # Ground Units
            self.max_zealot = 10
            self.max_stalker = 20
            self.max_adept = 10
            self.max_immortal = 4
            self.max_sentry = 3
            self.max_warpprism = 3
            self.max_colossus = 3
            self.max_disruptor = 1
            self.max_hightemplar = 6
            self.max_darktemplar = 6
            self.max_archon = 6

            # Air Units
            self.max_observer = 5
            self.max_phoenix = 3
            self.max_voidray = 8
            self.max_tempest = 4

        elif self.opponent == self.opponent_race['protoss']:
            if self.techPriority == 0:
                self.techPriority = self.tech['Templar']
                self.techSecondary = self.tech['Robo']
            if self.gamePhase != self.phase['Late']:
                self.max_zealot = 2
                self.max_stalker = 20
                self.max_colossus = 3

                self.max_phoenix = 3
            elif self.gamePhase == self.phase['Late']:
                self.max_zealot = 0
                self.max_stalker = 10
                self.max_colossus = 0

                self.max_phoenix = 6
            # Ground Units
            self.max_warpprism = 2
            self.max_adept = 0
            self.max_immortal = 5
            self.max_disruptor = 2
            self.max_sentry = 4
            self.max_hightemplar = 12
            self.max_darktemplar = 0
            self.max_archon = 10

            # Air Units
            self.max_observer = 2
            self.max_voidray = 16
            self.max_tempest = 8


        elif self.opponent == self.opponent_race['terran']:
            if self.techPriority == 0:
                self.techPriority = self.tech['Robo']
                self.techSecondary = self.tech['Templar']
            if self.gamePhase != self.phase['Late']:
                self.max_zealot = 6
                self.max_stalker = 25
                self.max_colossus = 3
            elif self.gamePhase == self.phase['Late']:
                self.max_zealot = 0
                self.max_stalker = 20
                self.max_colossus = 4
            # Ground Units
            self.max_warpprism = 2
            self.max_adept = 8
            self.max_immortal = 4
            self.max_disruptor = 3
            self.max_sentry = 4
            self.max_hightemplar = 12
            self.max_darktemplar = 4
            self.max_archon = 8

            # Air Units
            self.max_observer = 2
            self.max_phoenix = 6
            self.max_voidray = 16
            self.max_tempest = 8


        elif self.opponent == self.opponent_race['zerg']:
            if self.techPriority == 0:
                self.techPriority = self.tech['Robo']
                self.techSecondary = self.tech['Robo']

            if self.gamePhase != self.phase['Late']:
                self.max_zealot = 1
                self.max_stalker = 20
                self.max_adept = 10
                self.max_immortal = 4
                self.max_sentry = 4

                self.max_voidray = 3
            elif self.gamePhase == self.phase['Late']:
                self.max_zealot = 0
                self.max_stalker = 25
                self.max_adept = 0
                self.max_immortal = 6
                self.max_sentry = 4
                self.max_voidray = 16

            # Ground Units
            self.max_adept = 8
            self.max_colossus = 3
            self.max_disruptor = 3
            self.max_hightemplar = 10
            self.max_darktemplar = 0
            self.max_archon = 12

            # Air Units
            self.max_observer = 3
            self.max_warpprism = 2
            self.max_phoenix = 3
            self.max_tempest = 8

        # 1/X
        self.defenders = {ZEALOT: 10,
                          STALKER: 10
                          }

        self.army_size_defense = 0
        self.army_size_attack = 0
        self.UnitTierMidAmount = 0
        self.UnitTierHighAmount = 0

        for unit in self.army_weight:
            if self.units(unit).amount > 0:
                self.army_size_defense = self.army_size_defense + self.units(unit).amount * self.army_weight[unit]
                if unit != PROBE:
                    self.army_size_attack = self.army_size_attack + self.units(unit).amount * self.army_weight[unit]
                    # jos on mid-tierin joukkoa olemassa
                    if unit.name.lower() in self.unitTierList['Mid']:
                        self.UnitTierMidAmount = self.UnitTierMidAmount + self.units(unit).amount
                    # Jos on high-tierin joukkoa olemassa
                    elif unit.name.lower() in self.unitTierList['High']:
                        self.UnitTierHighAmount = self.UnitTierHighAmount + self.units(unit).amount


    async def unitRally(self, unit):
        special_list = ['warpprism', 'disruptor']
        if self.ArmyStatus == self.status['attacking']:
            if self.AttackingArmyStatus == self.AttackingArmyStatusList['Moving to Forward Rally 1']:
                if not self.known_enemy_units.closer_than(8, unit) and unit.distance_to(self.RallyPoint[1]) > 2:
                    if len(self.RallyPoint) >= 2:
                        self.actions.append(unit.move(self.RallyPoint[1]))

            elif self.AttackingArmyStatus == self.AttackingArmyStatusList['Moving to Forward Rally 2']:
                if not self.known_enemy_units.closer_than(8, unit) and unit.distance_to(self.RallyPoint[2]) > 2:
                    if len(self.RallyPoint) >= 3:
                        self.actions.append(unit.move(self.RallyPoint[2]))

            elif self.AttackingArmyStatus == self.AttackingArmyStatusList['Moving to Forward Rally 3']:
                if not self.known_enemy_units.closer_than(8, unit) and unit.distance_to(self.RallyPoint[3]) > 2:
                    if len(self.RallyPoint) >= 4:
                        self.actions.append(unit.move(self.RallyPoint[3]))

            elif self.AttackingArmyStatus == self.AttackingArmyStatusList['Commencing Attack']:
                enemy = self.known_enemy_units
                if enemy.exists:
                    if not self.known_enemy_units.closer_than(10, unit) and not unit.name.lower() in special_list:
                        if self.diversionAttack == 1:
                            self.actions.append(unit.move(self.known_enemy_units.closest_to(self.MainArmyTarget)))
                        else:
                            self.actions.append(unit.move(self.known_enemy_units.closest_to(unit)))
                    if not self.known_enemy_units.closer_than(12, unit) and unit.name.lower() in special_list:
                        if self.diversionAttack == 1:
                            self.actions.append(unit.move(self.MainArmyTarget))
                        else:
                            self.actions.append(unit.move(self.known_enemy_units.closest_to(unit)))
                else:
                    self.actions.append(unit.move(self.enemy_start_locations[0]))

            elif self.known_enemy_units.closer_than(8, unit) and self.AttackingArmyStatus != self.AttackingArmyStatusList['Commencing Attack']:
                self.AttackingArmyStatus = self.AttackingArmyStatusList['Under Attack']
                self.BattleLocation = unit.position



    async def forwardRally(self):
        if self.ArmyStatus == self.status['attacking']:
            if self.AttackingArmyStatus == self.AttackingArmyStatusList['Moving to Forward Rally 1']:
                if len(self.RallyPoint) >= 2:
                    if self.units.closer_than(6, self.RallyPoint[1]).amount > (self.attackUnitAmount * 0.5) and not self.Rallypoint_timer:
                        self.Rallypoint_timer = self.time

                    if self.units.closer_than(10, self.RallyPoint[1]).amount > (self.attackUnitAmount*0.9):
                        if len(self.RallyPoint) >= 3:
                            self.AttackingArmyStatus = self.AttackingArmyStatusList['Moving to Forward Rally 2']
                            self.Rallypoint_timer = 0
                        else:
                            self.AttackingArmyStatus = self.AttackingArmyStatusList['Commencing Attack']
                            self.Rallypoint_timer = 0

                    elif (self.time - self.Rallypoint_timer) > 20 and self.Rallypoint_timer:
                        # Force units to next rally to unstuck
                        if len(self.RallyPoint) >= 3:
                            self.AttackingArmyStatus = self.AttackingArmyStatusList['Moving to Forward Rally 2']
                            self.Rallypoint_timer = 0
                        else:
                            self.AttackingArmyStatus = self.AttackingArmyStatusList['Commencing Attack']
                            self.Rallypoint_timer = 0

            elif self.AttackingArmyStatus == self.AttackingArmyStatusList['Moving to Forward Rally 2']:
                if len(self.RallyPoint) >= 3:
                    if self.units.closer_than(10, self.RallyPoint[2]).amount > (self.attackUnitAmount * 0.5) and not self.Rallypoint_timer:
                        self.Rallypoint_timer = self.time

                    if self.units.closer_than(8, self.RallyPoint[2]).amount > (
                            self.attackUnitAmount * 0.9):
                        if len(self.RallyPoint) >= 4:
                            self.AttackingArmyStatus = self.AttackingArmyStatusList['Moving to Forward Rally 3']
                            self.Rallypoint_timer = 0
                        else:
                            self.AttackingArmyStatus = self.AttackingArmyStatusList['Commencing Attack']
                            self.Rallypoint_timer = 0

                    elif self.time - self.Rallypoint_timer > 10 and self.Rallypoint_timer:
                        if len(self.RallyPoint) >= 4:
                        # Force units to next rally to unstuck
                            self.AttackingArmyStatus = self.AttackingArmyStatusList['Moving to Forward Rally 3']
                            self.Rallypoint_timer = 0
                        else:
                            self.AttackingArmyStatus = self.AttackingArmyStatusList['Commencing Attack']
                            self.Rallypoint_timer = 0

                    elif self.known_enemy_units.closer_than(8, self.RallyPoint[2]).amount > 6:
                        self.AttackingArmyStatus = self.AttackingArmyStatusList['Commencing Attack']
                        self.Rallypoint_timer = 0
                else:
                    self.AttackingArmyStatus = self.AttackingArmyStatusList['Commencing Attack']
                    self.Rallypoint_timer = 0

            elif self.AttackingArmyStatus == self.AttackingArmyStatusList['Moving to Forward Rally 3']:
                if self.units.closer_than(10, self.RallyPoint[3]).amount > (self.attackUnitAmount * 0.5) and not self.Rallypoint_timer:
                    self.Rallypoint_timer = self.time

                if self.units.closer_than(8, self.RallyPoint[3]).amount > (
                        self.attackUnitAmount * 0.9):
                    self.AttackingArmyStatus = self.AttackingArmyStatusList['Commencing Attack']
                    self.Rallypoint_timer = 0

                elif self.known_enemy_units.closer_than(8, self.RallyPoint[3]).amount > 6:
                    self.AttackingArmyStatus = self.AttackingArmyStatusList['Commencing Attack']
                    self.Rallypoint_timer = 0

                elif self.time - self.Rallypoint_timer > 10 and self.Rallypoint_timer:
                    # Force units to next rally to unstuck
                    self.AttackingArmyStatus = self.AttackingArmyStatusList['Commencing Attack']
                    self.Rallypoint_timer = 0

            elif self.AttackingArmyStatus == self.AttackingArmyStatusList['Under Attack']:
                if not self.known_enemy_units.not_structure.closer_than(10, self.BattleLocation):
                    self.BattleLocation = 0
                    # Recalculate our attack force
                    self.attackUnitAmount = self.units.not_structure.exclude_type(PROBE).amount
                    self.AttackingArmyStatus = self.AttackingArmyStatusList['Moving to Forward Rally 2']



    # List of unit functions here
    async def ArmyManager(self):
        if self.attacking == 1:
            self.ArmyStatus = self.status['attacking']
            if self.enemy_expansions:
                self.enemy_expansions.sort(key=lambda x: x.distance_to(self.start_location))
                self.MainArmyTarget = self.enemy_expansions[0]
            else:
                self.MainArmyTarget = self.enemy_start_locations[0]

       # elif self.ArmyStatus == self.status['harassing']:


        for unit in self.units(ZEALOT):
            await self.zealot_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(DARKTEMPLAR):
            await self.darktemplar_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(STALKER):
            await self.stalker_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(ADEPT):
            await self.adept_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(IMMORTAL):
            await self.immortal_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(HIGHTEMPLAR):
            await self.hightemplar_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(OBSERVER):
            if unit.tag == self.scout:
                pass
            else:
                await self.observer_behaviour(unit)
                await self.ArmyBehaviour(unit)

        for unit in self.units(SENTRY):
            await self.sentry_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(WARPPRISM):
            await self.warpprismTransport_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(WARPPRISMPHASING):
            await self.warpprismPhasing_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(DISRUPTOR):
            await self.disruptor_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(DISRUPTORPHASED):
            await self.disruptor_nova(unit)

        for unit in self.units(COLOSSUS):
            await self.colossus_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(ARCHON):
            await self.archon_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(PHOENIX):
            await self.phoenix_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(VOIDRAY):
            await self.voidray_behaviour(unit)
            await self.ArmyBehaviour(unit)

        for unit in self.units(TEMPEST):
            await self.tempest_behaviour(unit)
            await self.ArmyBehaviour(unit)



    async def ArmyBehaviour(self, unit):
        # If a unit is further than 8 from rallypoint and idling, move to rallypoint
        if self.ArmyStatus != self.status['attacking'] or self.ArmyStatus != self.status['harassing']:
            if unit.is_idle and unit.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(unit.move(self.RallyPoint[0]))



    async def ArmyStatusManager(self):
        # Lähetä pallo (ja täydennä sitä), jos armyn arvo ylittää tietyn thresholdin
        if self.ArmyStatus == self.status['idling'] or self.ArmyStatus == self.status['harassing']:
            if (((self.army_size_attack > min(150, self.iteration_multiplier * 5) or self.supply_used > 180)) or
            (self.army_size_attack > min(100, self.iteration_multiplier * 4) and self.diversionAttack) == 1 or
            (self.army_size_attack > min(150, self.iteration_multiplier * 4) and
             len(self.enemy_expansions) > len(self.owned_expansions ) + 1)):
                self.attacking = 1
                self.attack_value = self.army_size_attack
                self.attackUnitAmount = self.units.not_structure.exclude_type(PROBE).amount
                self.AttackingArmyStatus = self.AttackingArmyStatusList['Moving to Forward Rally 1']

#        if self.army_size_attack > min(100, self.iteration_multiplier * 3) and self.ArmyStatus != self.status['defending']:
 #           self.ArmyStatus = self.status['harassing']
  #          self.attackUnitAmount = self.units.not_structure.exclude_type(PROBE).amount

        if self.attacking == 1:
            #Jos alle kolmasosa hengissä, lopeta ns. jatkuva hyökkäys ja ala keräämään uutta palloa
            if self.army_size_attack < self.attack_value / 3 and self.known_enemy_units.not_structure.exclude_type(self.enemyWorker).amount > 2:
                self.attacking = 0
                self.AttackingArmyStatus = self.AttackingArmyStatusList['Moving to Forward Rally 1']

        # If there's troops outside the base when we're not defending or attacking
        if self.attacking == 0 and not self.ArmyStatus == self.status['defending'] and \
                not self.ArmyStatus == self.status['harassing'] and \
                self.units.not_structure.exclude_type(PROBE).further_than(30, self.RallyPoint[0]):
            # Rally command issued, set status to 0
            self.ArmyStatus = self.status['rallying']

        # If we're rallying and most of the troops are in rallypoint, then switch to idling
        if self.ArmyStatus == self.status['rallying'] and self.units.not_structure.exclude_type(PROBE).further_than \
                    (25, self.RallyPoint[0]).amount < 3:
            # Rally complete
            self.ArmyStatus = self.status['idling']

        for nexus in self.units(NEXUS):
            enemiesCloseToBase = self.known_enemy_units.closer_than(self.def_range, nexus)
            # If there are enemies close to base, then def
            if enemiesCloseToBase.amount > 1:
                self.ArmyStatus = self.status['defending']
                self.defend_target = nexus
                self.attacking = 0
                # Let's see if this stops probes from attacking enemy base
            # if we're in defend state and there are no longer enemies close to base, then switch to idle
            elif self.ArmyStatus == self.status['defending'] and not self.known_enemy_units.closer_than(25, self.defend_target):
                self.ArmyStatus = self.status['idling']
                self.defend_target = None


    async def TaskForce(self):
        if self.time < 360:
            self.taskForceObjective = self.Objective['Adept_harass']
            if self.units(ADEPT).amount > 1 and not self.ArmyStatus == self.status['defending'] and len(self.taskForce) < 2:
                if len(self.ExpansionHarassList) < 3:
                    self.ExpansionHarassList = [Point2(x) for x in self.possible_enemy_locations if x.distance_to(self.enemy_start_locations[0]) < 50]
                    self.ExpansionHarassList.sort(key=lambda x: x.distance_to(self.enemy_start_locations[0]), reverse=True)
                if len(self.taskForce) < 2:
                    adept = self.units(ADEPT).random.tag
                    if not adept in self.taskForce:
                        self.taskForce.append(adept)
            # Disband taskforce if enemies are attacking
            if self.ArmyStatus == self.status['defending']:
                self.taskForce = []
        else:
            self.taskForceObjective = self.Objective['WarpPrism_strike']
            if self.units(WARPPRISM).exists and (self.units(DISRUPTOR).amount > 1 or
                (self.units(ZEALOT).amount + self.units(ADEPT).amount) > 3) and not self.taskForce \
                    and len(self.enemy_expansions) > 2 and self.ArmyStatus == self.status['idling']:
                self.taskForce.append(self.units(WARPPRISM).closest_to(self.RallyPoint[0]).tag)
                if self.units(DISRUPTOR).amount > 1:
                    self.taskForce_type = self.forcetype['disruptor']
                elif (self.units(ZEALOT).amount + self.units(ADEPT).amount) > 3:
                    self.taskForce_type = self.forcetype['gateway_units']

            self.enemy_expansions.sort(key=lambda x: x.distance_to(self.enemy_start_locations[0]), reverse=True)
            enemy_ground_def = self.known_enemy_structures.filter(lambda x: x.can_attack_ground)
            target_number = 0
            for target in self.enemy_expansions:
                if enemy_ground_def.closer_than(10, target):
                    if len(self.enemy_expansions) < target_number + 1:
                        target_number = target_number + 1
                    else:
                        # No targets, disband
                        self.taskForceSignal = 2
                else:
                    self.taskForceTarget = target
                    break
            # If warp prism is ded
            if self.taskForce:
                if not self.units.find_by_tag(self.taskForce[0]):
                    self.taskForce = []
                    self.diversionAttack = 0



    async def probe_behaviour(self):
        if self.ArmyStatus == self.status['defending']:
            self.workerstatus = self.probestatus['JESUSTAKETHEWHEEL']

        if self.workerstatus == self.probestatus['JESUSTAKETHEWHEEL']:
            for nexus in self.units(NEXUS).ready:
                if self.known_enemy_units.not_flying.closer_than(self.def_range, nexus).amount > 0:
#Jos pyloneita lähellä basea --> cannon rush --> tuhotaan pylonit
                    vihunPylonit = self.known_enemy_structures.filter(lambda x: x.name.lower() == 'pylon').closer_than(self.def_range, nexus)
                    vihunWorkerit = self.known_enemy_units.filter(lambda x: x.name.lower() == 'probe').closer_than(self.def_range, nexus)
                    if vihunPylonit.exists or vihunWorkerit.exists:
                        if vihunWorkerit.exists:
                            target = vihunWorkerit.first
                        else:
                            target = vihunPylonit.first

                        nexuksenProbet = self.workers.closer_than(self.def_range, nexus)
                        for worker in nexuksenProbet.take(min(5,len(nexuksenProbet))):
                            # 5 tai niin monta kuin hengissä hyökkää pyloniin, duh
                            self.actions.append(worker.attack(target))
                    else:
                        enemiesCloseToBase = self.known_enemy_units.closer_than(20, nexus)
                        nexuksenProbet = self.workers.closer_than(self.def_range, nexus)
                    # muiden puolustajien määrä
                        AmountOfDefenders = self.units.not_structure.exclude_type({PROBE}).closer_than(self.def_range,nexus).amount
                        if nexuksenProbet.exists:
                        # ota n kappaletta probeja, jossa n on vihujen määrä - non-probe puolustajien +1 (max estääkseen neg luvut)
                        # Jos enemmän vihuja kun probeja, ota kaikki kynnelle kykenevät
                            if enemiesCloseToBase.amount - AmountOfDefenders + 1 > nexuksenProbet.amount:
                                amountOfProbes = nexuksenProbet.amount
                            else:
                                amountOfProbes = max(enemiesCloseToBase.amount - AmountOfDefenders + 1, 0)
                            for worker in nexuksenProbet.take(amountOfProbes):
                            # kaikki ottaa uuden kohteen, lähimmän
                                self.actions.append(worker.attack(self.find_GroundTarget(worker)))
                else:
                    self.workerstatus = self.probestatus['neutral']

        elif self.workerstatus == self.probestatus['neutral']:
            for a in self.workers:
                lahin_nexus = self.units(NEXUS).ready.closest_to(a)
                if (a.is_moving or a.is_attacking) and a.distance_to(lahin_nexus) < 3:
                    self.actions.append(a.stop())
                elif a.distance_to(self.units(NEXUS).closest_to(a)) > 10 and (a.is_returning or a.is_attacking):
                    if a.tag == self.scout and a.is_returning == False:
                        return
                    else:    
                        self.actions.append(a.move(lahin_nexus.position))


    async def zealot_behaviour(self, zealot):
        if zealot.tag in self.taskForce:
            if zealot.distance_to(self.RallyPoint[0]) < 25 or self.taskForceSignal == 1:
                #warpprism = self.taskForce.filter(key= lambda x: self.units.by_tag(x).name.lower() == 'warpprism')[0]
                #warpprism = [x for x in self.taskForce if self.units.find_by_tag(x).name.lower() == 'warpprism'][0]
                warpprism = 0
                for unit in self.taskForce:
                    if self.units.find_by_tag(unit).exists:
                        unit = self.units.find_by_tag(unit)
                        if unit.name.lower() == 'warpprism':
                            warpprism = unit
                if warpprism:
                    warpprism = self.units.by_tag(warpprism)
                    self.actions.append(zealot.move(warpprism.position))

            else:
                if self.known_enemy_units.not_structure.exclude_type(self.enemyWorker).amount > 3:
                    self.taskForceSignal = 1
                else:
                    if self.known_enemy_units:
                        self.actions.append(zealot.attack(self.known_enemy_units.not_structure.closest_to(zealot)))
                    else:
                        self.actions.append(zealot.attack(self.known_enemy_units.closest_to(zealot)))
        else:
            if self.ArmyStatus == self.status['rallying']:
                if zealot.distance_to(self.RallyPoint[0]) > 8:
                    self.actions.append(zealot.move(self.RallyPoint[0]))
                    return
            #Check for low health nearby enemies
            enemyUnitsClose = self.known_enemy_units.not_flying.exclude_type(UnitTypeId.EGG).closer_than(1, zealot)
            # Attacks enemies with lowest HP near zealot
            if zealot.weapon_cooldown == 0 and enemyUnitsClose.exists:
                enemyUnits = enemyUnitsClose.sorted(lambda x: x.health_percentage)
                closestEnemy = enemyUnits[0]
                self.actions.append(zealot.attack(closestEnemy))
                return # continue for loop, dont execute any of the following

            elif self.ArmyStatus == self.status['attacking']:
                if self.known_enemy_units.closer_than(12,zealot):
                    self.actions.append(zealot.attack(self.find_GroundTarget(zealot)))
                else:
                    await self.unitRally(zealot)
            elif self.ArmyStatus == self.status['defending']:
                self.actions.append(zealot.attack(self.find_GroundTarget(zealot)))
            elif self.ArmyStatus == self.status['harassing']:
                if not self.known_enemy_units.not_structure.exclude_type\
                            ([UnitTypeId.EGG, UnitTypeId.LARVA, self.enemyWorker]).closer_than(7, zealot).amount > 4:
                    self.find_ExpansionTargets(zealot)
                elif self.known_enemy_units.not_structure.exclude_type \
                                   ([UnitTypeId.EGG, UnitTypeId.LARVA, self.enemyWorker]).closer_than(7,
                                                                                                      zealot).amount > 8:
                    self.ArmyStatus = self.status['rallying']
                else:
                    self.actions.append(zealot.move(self.RallyPoint[0]))

    async def darktemplar_behaviour(self, darktemplar):

        if self.ArmyStatus == self.status['rallying']:
            if darktemplar.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(darktemplar.move(self.RallyPoint[0]))
                return

        if self.units(UnitTypeId.DARKTEMPLAR).idle.ready.amount >= 2 and (darktemplar.energy < 50 or darktemplar.health_percentage <= 4 / 10):
            dt1 = darktemplar
            dt2 = next((dt for dt in self.units(UnitTypeId.DARKTEMPLAR) if dt.tag != dt1.tag and (dt.energy < 50 or dt.health_percentage <= 4 / 10)), None)
            if dt2:
               # await self.chat_send(
                #    "Sending morph command, morph archon ability value == {}".format(AbilityId.MORPH_ARCHON.value))
                from s2clientprotocol import raw_pb2 as raw_pb
                from s2clientprotocol import sc2api_pb2 as sc_pb
                command = raw_pb.ActionRawUnitCommand(
                    ability_id=AbilityId.MORPH_ARCHON.value,
                    unit_tags=[dt1.tag, dt2.tag],
                    queue_command=False)
                action = raw_pb.ActionRaw(unit_command=command)
                await self._client._execute(action=sc_pb.RequestAction(
                    actions=[sc_pb.Action(action_raw=action)]))
                return
        # if self.units(UnitTypeId.ARCHON).amount > 0:
          #  await self.chat_send("Archon detected!")

        #Check for low health nearby enemies
        enemyUnitsClose = self.known_enemy_units.not_flying.exclude_type(UnitTypeId.EGG).closer_than(1, darktemplar)
        # Attacks enemies with lowest HP near zealot
        if darktemplar.weapon_cooldown == 0 and enemyUnitsClose.exists:
            enemyUnits = enemyUnitsClose.sorted(lambda x: x.health_percentage)
            closestEnemy = enemyUnits[0]
            self.actions.append(darktemplar.attack(closestEnemy))
            return # continue for loop, dont execute any of the following
        elif self.ArmyStatus == self.status['attacking']:
            if self.known_enemy_units.closer_than(12,darktemplar):
                self.actions.append(darktemplar.attack(self.find_GroundTarget(darktemplar)))
            else:
                await self.unitRally(darktemplar)
        elif self.ArmyStatus == self.status['defending']:
            self.actions.append(darktemplar.attack(self.find_GroundTarget(darktemplar)))
        elif self.ArmyStatus == self.status['harassing']:
            if not self.known_enemy_units.not_structure.exclude_type \
                               ([UnitTypeId.EGG, UnitTypeId.LARVA, self.enemyWorker]).closer_than(7, darktemplar).amount > 4:
                self.find_ExpansionTargets(darktemplar)
            elif self.known_enemy_units.not_structure.exclude_type \
                        ([UnitTypeId.EGG, UnitTypeId.LARVA, self.enemyWorker]).closer_than(7,
                                                                                           darktemplar).amount > 8:
                self.ArmyStatus = self.status['rallying']
            else:
                self.actions.append(darktemplar.move(self.RallyPoint[0]))


    async def stalker_behaviour(self, stalker):

        if self.ArmyStatus == self.status['rallying']:
            if stalker.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(stalker.move(self.RallyPoint[0]))
                return

        enemyThreatsClose = self.known_enemy_units.not_structure.closer_than(6, stalker)
        abilities = (await self.get_available_abilities(stalker))
        # Blink micro condition
        if enemyThreatsClose.exists and stalker.shield_percentage < 1 / 10 and AbilityId.EFFECT_BLINK_STALKER in abilities:
            # Get position furthest from closest enemy towards rallypoint (later improve it)
            closestEnemy = enemyThreatsClose.closest_to(stalker)
            # hard-coded range to 3 in order to get back to the fight faster (needs testing)
            retreatPoint = stalker.position.towards(closestEnemy, distance=-3)

            # If we can cast blink, then cast, topkek
            if await self.can_cast(stalker, AbilityId.EFFECT_BLINK_STALKER, retreatPoint,
                                   cached_abilities_of_unit=abilities):
                blink_ready = 1
                # Cast blink. WIP, needs modification of blink location
                if blink_ready:
                    self.actions.append(stalker(AbilityId.EFFECT_BLINK_STALKER, retreatPoint))
                    return


        # move towards to max unit range if enemy is closer than 5
        enemyThreatsVeryClose = self.known_enemy_units.not_structure.closer_than(5.9, stalker) # hardcoded attackrange minus 0.5

        # threats that can attack the stalker
        if stalker.weapon_cooldown != 0 and enemyThreatsVeryClose.exists:
            retreatPoints = self.neighbors8(stalker.position, distance=2) | self.neighbors8(stalker.position, distance=4)
            # filter points that are pathable by a stalker
            retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
            if retreatPoints:
                closestEnemy = enemyThreatsVeryClose.closest_to(stalker)
                retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(stalker))
                #retreatPoint = closestEnemy.position.furthest(retreatPoints)
                self.actions.append(stalker.move(retreatPoint))
                return # continue loop, don't execute any of the following


        enemyUnits = self.known_enemy_units.not_structure.exclude_type(UnitTypeId.EGG).closer_than(6, stalker) # hardcoded attackrange of 6
        # If stalker can attack and enemies are close, attac closest
        if stalker.weapon_cooldown == 0 and enemyUnits.exists:
            enemyUnits = enemyUnits.sorted(lambda x: x.distance_to(stalker))
            closestEnemy = enemyUnits[0]
            self.actions.append(stalker.attack(closestEnemy))
            return # continue for loop, dont execute any of the following
            # If no targets nearby, initiate attack command
        elif self.ArmyStatus == self.status['attacking']:
            if self.known_enemy_units.closer_than(12, stalker):
                self.find_AnyTarget(stalker)
            else:
                await self.unitRally(stalker)
        elif self.ArmyStatus == self.status['defending']:
            self.actions.append(stalker.attack(self.find_AnyTarget(stalker)))
        elif self.ArmyStatus == self.status['harassing']:
            if not self.known_enemy_units.not_structure.exclude_type \
                               ([UnitTypeId.EGG, UnitTypeId.LARVA, self.enemyWorker]).closer_than(7, stalker).amount > 4:
                self.find_ExpansionTargets(stalker)
                print("harassing")
            elif self.known_enemy_units.not_structure.exclude_type \
                        ([UnitTypeId.EGG, UnitTypeId.LARVA, self.enemyWorker]).closer_than(7,
                                                                                           stalker).amount > 8:
                self.ArmyStatus = self.status['rallying']
            else:
                self.actions.append(stalker.move(self.RallyPoint[0]))
                print("enemies close")
    


    async def adept_behaviour(self, adept):
        if adept.tag in self.taskForce:
            await self.adept_taskForce_behaviour(adept)
        else:

            if self.ArmyStatus == self.status['rallying']:
                if adept.distance_to(self.RallyPoint[0]) > 8:
                    self.actions.append(adept.move(self.RallyPoint[0]))
                    return

            enemyUnits = self.known_enemy_units.not_structure.closer_than(4, adept)  # hardcoded attackrange of 6
            enemyThreatsClose = self.known_enemy_units.not_structure.exclude_type(UnitTypeId.EGG).closer_than(3.9, adept)
            abilities = (await self.get_available_abilities(adept))

            # Shade micro condition
    #        if AbilityId.EFFECT_PSIONICTRANSFER in abilities:
                # If we can cast blink, then cast, topkek
    #            if await self.can_cast(immortal, AbilityId.EFFECT_IMMORTALBARRIER,
      #                                 cached_abilities_of_unit=abilities):
     #               shield_ready = 1
                    # Cast blink. WIP, needs modification of blink location
       #             if shield_ready:
        #                self.actions.append(immortal(AbilityId.EFFECT_IMMORTALBARRIER))
         #               return
            
            if adept.weapon_cooldown != 0 and enemyThreatsClose.exists:
                retreatPoints = self.neighbors8(adept.position, distance=2) | self.neighbors8(adept.position,
                                                                                                distance=4)
                # filter points that are pathable by a adept
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreatsClose.closest_to(adept)
                    retreatPoint = max(retreatPoints,
                                    key=lambda x: x.distance_to(closestEnemy))
                    # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                    self.actions.append(adept.move(retreatPoint))
                    return  # continue for loop, don't execute any of the following

            # If stalker can attack and enemies are close, attac closest
            elif adept.weapon_cooldown == 0 and enemyUnits.exists:
                enemyUnits = enemyUnits.sorted(lambda x: x.distance_to(adept))
                closestEnemy = enemyUnits[0]
                self.actions.append(adept.attack(closestEnemy))
                return  # continue for loop, dont execute any of the following
            # If no targets nearby, initiate attack command
            elif self.ArmyStatus == self.status['attacking']:
                if self.known_enemy_units.closer_than(12,adept):
                    self.actions.append(adept.attack(self.find_AnyTarget(adept)))
                else:
                    await self.unitRally(adept)
            elif self.ArmyStatus == self.status['defending']:
                self.actions.append(adept.attack(self.find_AnyTarget(adept)))
            elif self.ArmyStatus == self.status['harassing']:
                if not self.known_enemy_units.not_structure.exclude_type \
                                   ([UnitTypeId.EGG, UnitTypeId.LARVA, self.enemyWorker]).closer_than(7,
                                                                                                      adept).amount > 4:
                    self.find_ExpansionTargets(adept)
                elif self.known_enemy_units.not_structure.exclude_type \
                                   ([UnitTypeId.EGG, UnitTypeId.LARVA, self.enemyWorker]).closer_than(7,
                                                                                                      adept).amount > 8:
                    self.ArmyStatus = self.status['rallying']
                else:
                    self.actions.append(adept.move(self.RallyPoint[0]))



    async def adept_taskForce_behaviour(self, adept):
        enemyworker = ['Probe', 'Scv', 'Drone']
        if self.taskForceObjective == self.Objective['Adept_harass'] and len(self.taskForce) > 1:
            enemyworker = ['Probe', 'Scv', 'Drone']
            vihut = self.known_enemy_units.exclude_type(UnitTypeId.EGG)
            abilities = await self.get_available_abilities(adept)

            if len(self.ExpansionHarassList) >= 1:
                mineral = self.ExpansionHarassTarget
                target = self.state.mineral_field.closest_to(mineral).position.towards(mineral, distance=-4)
                enemyThreatsClose = self.known_enemy_units.not_structure.exclude_type(
                    [UnitTypeId.EGG, self.enemyWorker]).closer_than(3.9, adept)
                enemyThreatsToMicro = self.known_enemy_units.not_structure.exclude_type(
                    [UnitTypeId.EGG, self.enemyWorker]).closer_than(7, adept)
                if adept.distance_to(target) > 9:

                    if vihut.closer_than(8, adept) and adept.weapon_cooldown == 0:

                        # Go to next mineral line
                        if AbilityId.ADEPTPHASESHIFT_ADEPTPHASESHIFT in abilities and \
                                adept.distance_to(target) > 12:
                            # If we can cast shade, then cast, topkek
                            if await self.can_cast(adept, AbilityId.ADEPTPHASESHIFT_ADEPTPHASESHIFT, target,
                                                cached_abilities_of_unit=abilities):
                                transfer_ready = 1
                                if transfer_ready:
                                    self.actions.append(adept(AbilityId.ADEPTPHASESHIFT_ADEPTPHASESHIFT, target))
                                    return

                        if enemyThreatsClose.amount > 2 and not await self.can_cast(adept, AbilityId.ADEPTPHASESHIFT_ADEPTPHASESHIFT):
                            retreatPoints = self.neighbors8(adept.position, distance=2) | self.neighbors8(adept.position,
                                                                                                            distance=4)
                            # filter points that are pathable by a adept
                            retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                            if retreatPoints:
                                closestEnemy = enemyThreatsClose.closest_to(adept)
                                retreatPoint = max(retreatPoints,
                                                key=lambda x: x.distance_to(closestEnemy) - x.distance_to(adept))
                                # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                                self.actions.append(adept.move(retreatPoint))
                                return  # continue for loop, don't execute any of the following

                        elif enemyThreatsToMicro.exists and adept.weapon_cooldown != 0:
                            retreatPoints = self.neighbors8(adept.position, distance=2) | self.neighbors8(adept.position,
                                                                                                            distance=4)
                            # filter points that are pathable by a adept
                            retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                            if retreatPoints:
                                closestEnemy = enemyThreatsClose.closest_to(adept)
                                retreatPoint = max(retreatPoints,
                                                key=lambda x: x.distance_to(closestEnemy) - x.distance_to(adept))
                                # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                                self.actions.append(adept.move(retreatPoint))
                                return  # continue for loop, don't execute any of the following

                        if vihut.not_structure.closer_than(8, adept).filter(
                            lambda x: x.name in enemyworker).exists and adept.weapon_cooldown == 0:
                            self.actions.append(adept.attack(vihut.not_structure.filter(lambda x: x.name in enemyworker).closest_to(
                            adept)))
                        else:
                            self.actions.append(adept.move(target))

                    else:
                        self.actions.append(adept.move(target))

                        # Go to next mineral line
                        if AbilityId.ADEPTPHASESHIFT_ADEPTPHASESHIFT in abilities and \
                                adept.distance_to(target) > 14:
                            # If we can cast shade, then cast, topkek
                            if await self.can_cast(adept, AbilityId.ADEPTPHASESHIFT_ADEPTPHASESHIFT, target,
                                                cached_abilities_of_unit=abilities):
                                transfer_ready = 1
                                if transfer_ready:
                                    self.actions.append(adept(AbilityId.ADEPTPHASESHIFT_ADEPTPHASESHIFT, target))
                                    return
                # Jos Adept tarpeeksi lähellä kohdetta
                else:                    
                    if (vihut.not_structure.exclude_type(self.enemyWorker).closer_than(6, target).amount > 2) or \
                        (adept.shield_percentage < 1/10 and adept.health_percentage < 8/10):
                        next_mineral_line = self.enemy_start_locations[0]
                        for minerals in self.ExpansionHarassList:
                            if adept.distance_to(minerals) > 10:
                                next_mineral_line = self.state.mineral_field.closest_to(minerals).position.towards(minerals, distance=-4)
                                break
                        enemyThreatsClose = self.known_enemy_units.not_structure.exclude_type([UnitTypeId.EGG, self.enemyWorker]).closer_than(3.9, adept)

                        # Go to next mineral line
                        if AbilityId.ADEPTPHASESHIFT_ADEPTPHASESHIFT in abilities:
                            # If we can cast shade, then cast, topkek
                            if await self.can_cast(adept, AbilityId.ADEPTPHASESHIFT_ADEPTPHASESHIFT, next_mineral_line,
                                                cached_abilities_of_unit=abilities):
                                transfer_ready = 1
                                if transfer_ready:
                                    self.actions.append(adept(AbilityId.ADEPTPHASESHIFT_ADEPTPHASESHIFT, next_mineral_line))

                        if (adept.weapon_cooldown != 0 and enemyThreatsClose.exists) or enemyThreatsClose.amount > 4:
                            retreatPoints = self.neighbors8(adept.position, distance=2) | self.neighbors8(adept.position,
                                                                                                            distance=4)
                            # filter points that are pathable by a adept
                            retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                            if retreatPoints:
                                closestEnemy = enemyThreatsClose.closest_to(adept)
                                retreatPoint = max(retreatPoints,
                                                key=lambda x: x.distance_to(closestEnemy) - x.distance_to(adept))
                                # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                                self.actions.append(adept.move(retreatPoint))
                                return  # continue for loop, don't execute any of the following

                    if self.known_enemy_structures.closer_than(8, target):
                        if vihut.not_structure.closer_than(9, adept).filter(
                            lambda x: x.name in enemyworker).exists:
                            self.actions.append(adept.attack(vihut.not_structure.filter(lambda x: x.name in enemyworker).closest_to(
                                adept)))
                        elif self.known_enemy_structures.exists:
                            self.actions.append(adept.attack(self.known_enemy_structures.closest_to(adept)))


                if not self.known_enemy_structures.closer_than(8, self.ExpansionHarassList[self.ExpansionHarassCounter]) \
                        and adept.distance_to(self.ExpansionHarassList[self.ExpansionHarassCounter]) < 9:
                    if len(self.ExpansionHarassList) > self.ExpansionHarassCounter + 1:
                        self.ExpansionHarassList.pop(self.ExpansionHarassCounter)
                        self.ExpansionHarassCounter = 0
                    else:
                        self.ExpansionHarassCounter = 0
                    self.ExpansionHarassTarget = self.ExpansionHarassList[self.ExpansionHarassCounter]

        
        elif self.taskForceObjective == self.Objective['WarpPrism_strike']:
            if adept.distance_to(self.RallyPoint[0]) < 25 or self.taskForceSignal == 1:
                warpprism = 0
                for unit in self.taskForce:
                    if self.units.find_by_tag(unit) != None:
                        unit = self.units.find_by_tag(unit)
                        if unit.name.lower() == 'warpprism':
                            warpprism = unit
                if warpprism:
                    warpprism = self.units.by_tag(warpprism)
                    self.actions.append(adept.move(warpprism.position))

            else:
                if self.known_enemy_units.not_structure.exclude_type(self.enemyWorker).amount > 3:
                    self.taskForceSignal = 1
                else:
                    if self.known_enemy_units.filter(lambda x: x.name in enemyworker):
                        self.actions.append(adept.attack(self.known_enemy_units.filter
                            (lambda x: x.name in enemyworker).closest_to(adept)))
                    elif self.known_enemy_units.filter(lambda x: x.is_structure).exists:
                        self.actions.append(adept.attack(self.known_enemy_units.filter
                                                        (lambda x: x.is_structure).closest_to(adept)))



    async def immortal_behaviour(self, immortal):
        if self.ArmyStatus == self.status['rallying']:
            if immortal.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(immortal.move(self.RallyPoint[0]))
                return

        enemyUnits = self.known_enemy_units.not_structure.closer_than(6, immortal)  # hardcoded attackrange of 6
        enemyThreatsClose = self.known_enemy_units.not_structure.exclude_type(UnitTypeId.EGG).closer_than(5.5, immortal)
        abilities = (await self.get_available_abilities(immortal))
        # Blink micro condition
        if enemyThreatsClose.exists and immortal.shield_percentage < 2 / 10 and AbilityId.EFFECT_IMMORTALBARRIER in abilities:

            # If we can cast blink, then cast, topkek
            if await self.can_cast(immortal, AbilityId.EFFECT_IMMORTALBARRIER,
                                   cached_abilities_of_unit=abilities):
                shield_ready = 1
                # Cast blink. WIP, needs modification of blink location
                if shield_ready:
                    self.actions.append(immortal(AbilityId.EFFECT_IMMORTALBARRIER))
                    return


        if immortal.weapon_cooldown != 0 and enemyThreatsClose.exists:
            retreatPoints = self.neighbors8(immortal.position, distance=1) | self.neighbors8(immortal.position,
                                                                                            distance=2)
            # filter points that are pathable by a stalker
            retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
            if retreatPoints:
                closestEnemy = enemyThreatsClose.closest_to(immortal)
                retreatPoint = max(retreatPoints,
                                   key=lambda x: x.distance_to(closestEnemy) - x.distance_to(immortal))
                # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                self.actions.append(immortal.move(retreatPoint))
                return  # continue for loop, don't execute any of the following

        # If immortal can attack and enemies are close, attac closest
        elif immortal.weapon_cooldown == 0 and enemyUnits.exists:
            enemyUnits = enemyUnits.sorted(lambda x: x.distance_to(immortal))
            closestEnemy = enemyUnits[0]
            self.actions.append(immortal.attack(closestEnemy))
            return  # continue for loop, dont execute any of the following
        # If no targets nearby, initiate attack command
        elif self.ArmyStatus == self.status['attacking']:
            if self.known_enemy_units.closer_than(12,immortal):
                self.actions.append(immortal.attack(self.find_GroundTarget(immortal)))
            else:
                await self.unitRally(immortal)
        elif self.ArmyStatus == self.status['defending']:
            self.actions.append(immortal.attack(self.find_GroundTarget(immortal)))
        elif self.ArmyStatus == self.status['harassing']:
            self.actions.append(immortal.attack(self.find_HarassTarget(immortal)))



    async def hightemplar_behaviour(self, hightemplar):

        if self.ArmyStatus == self.status['rallying']:
            if hightemplar.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(hightemplar.move(self.RallyPoint[0]))
                return

        if self.units(HIGHTEMPLAR).amount >= 2 and (hightemplar.energy < 50 or hightemplar.health_percentage <= 4 / 10):
            ht1 = hightemplar
            ht2 = next((ht for ht in self.units(HIGHTEMPLAR) if ht.tag != ht1.tag and (ht.energy < 50 or ht.health_percentage <= 4 / 10)), None)
            if ht2:
                #await self.chat_send(
                  #  "Sending morph command, morph archon ability value == {}".format(AbilityId.MORPH_ARCHON.value))
                from s2clientprotocol import raw_pb2 as raw_pb
                from s2clientprotocol import sc2api_pb2 as sc_pb
                command = raw_pb.ActionRawUnitCommand(
                    ability_id=AbilityId.MORPH_ARCHON.value,
                    unit_tags=[ht1.tag, ht2.tag],
                    queue_command=False)
                action = raw_pb.ActionRaw(unit_command=command)
                await self._client._execute(action=sc_pb.RequestAction(
                    actions=[sc_pb.Action(action_raw=action)]))
                return

        #if self.units(UnitTypeId.ARCHON).amount > 0:
         #   await self.chat_send("Archon detected!")

        enemyThreatsClose = self.known_enemy_units.not_structure.exclude_type(UnitTypeId.EGG).closer_than(6, hightemplar)
        abilities = (await self.get_available_abilities(hightemplar))
        targetlist = {'ghost', 'banshee', 'medivac', 'raven',
                      'hightemplar', 'sentry', 'phoenix', 'mothership', 'oracle',
                      'infestor', 'overseer', 'queen', 'viper'}

        # Psionic storm
        PsionicStormRange = self._game_data.abilities[AbilityId.PSISTORM_PSISTORM.value]._proto.cast_range
        UnitsInStormRange = self.known_enemy_units.not_structure.exclude_type([UnitTypeId.LARVA, UnitTypeId.EGG]).closer_than(PsionicStormRange, hightemplar)
        if UnitsInStormRange.exists and hightemplar.energy >= 75:
            UnitsInStormRange = UnitsInStormRange.sorted(lambda x: x.distance_to(hightemplar), reverse=True)
            furthestEnemy = None
            for enemy in UnitsInStormRange:
                if await self.can_cast(hightemplar, AbilityId.PSISTORM_PSISTORM, enemy.position, cached_abilities_of_unit=abilities):
                    if self.known_enemy_units.closer_than(1.5, enemy).amount > 2:
                        furthestEnemy = enemy.position
                        break
            if furthestEnemy:
                self.actions.append(hightemplar(AbilityId.PSISTORM_PSISTORM, furthestEnemy))
                return

                # Use it on enemy casters
        if AbilityId.FEEDBACK_FEEDBACK in abilities and enemyThreatsClose.exists:
            for target in enemyThreatsClose:
                if target.name.lower() in targetlist and target.energy >= 40:
                    self.actions.append(hightemplar(AbilityId.FEEDBACK_FEEDBACK, target))
                    return

#        if self.units(ARCHON).amount < self.max_archon and \
#            (self.units(HIGHTEMPLAR).closer_than(8, hightemplar) or self.units(DARKTEMPLAR).closer_than(8, hightemplar)) and\
#            not self.known_enemy_units.not_structure.closer_than(10, hightemplar):
#            if self.units(HIGHTEMPLAR).amount > 2:
#                self.actions.append(hightemplar.move(self.units(HIGHTEMPLAR).closest_to(hightemplar).position))
#            elif self.units(DARKTEMPLAR).exists:
#                self.actions.append(hightemplar.move(self.units(DARKTEMPLAR).closest_to(hightemplar).position))

        if AbilityId.RALLY_MORPHING_UNIT in abilities and self.units(ARCHON).amount < self.max_archon:
            self.actions.append(hightemplar(AbilityId.ARCHON_WARP_TARGET))
            return

        # move towards to max unit range if enemy is closer than 5
        enemyThreatsVeryClose = self.known_enemy_units.not_structure.closer_than(5.5,
                        hightemplar)  # hardcoded attackrange minus 0.5
        # threats that can attack the stalker
        if hightemplar.weapon_cooldown != 0 and enemyThreatsVeryClose.exists:
            retreatPoints = self.neighbors8(hightemplar.position, distance=1) | self.neighbors8(hightemplar.position,
                                                                                            distance=2)
            # filter points that are pathable by a stalker
            retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
            if retreatPoints:
                closestEnemy = enemyThreatsVeryClose.closest_to(hightemplar)
                retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(hightemplar))
                # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                self.actions.append(hightemplar.move(retreatPoint))
                return  # continue for loop, don't execute any of the following

        enemyUnits = self.known_enemy_units.not_structure.closer_than(6, hightemplar)  # hardcoded attackrange of 6
        # If stalker can attack and enemies are close, attac closest
        if hightemplar.weapon_cooldown == 0 and enemyUnits.exists:
            enemyUnits = enemyUnits.sorted(lambda x: x.distance_to(hightemplar))
            closestEnemy = enemyUnits[0]
            self.actions.append(hightemplar.attack(closestEnemy))
            return  # continue for loop, dont execute any of the following
        # If no targets nearby, initiate attack command
        elif self.ArmyStatus == self.status['attacking']:
            if self.known_enemy_units.closer_than(12,hightemplar):
                self.actions.append(hightemplar.attack(self.find_AnyTarget(hightemplar)))
            else:
                await self.unitRally(hightemplar)
        elif self.ArmyStatus == self.status['defending']:
            self.actions.append(hightemplar.attack(self.find_AnyTarget(hightemplar)))


    async def archon_behaviour(self, archon):
        if self.ArmyStatus == self.status['rallying']:
            if archon.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(archon.move(self.RallyPoint[0]))
                return

        enemyUnits = self.known_enemy_units.not_structure.exclude_type(UnitTypeId.EGG).closer_than(3, archon)  # hardcoded attackrange of 6
        # If stalker can attack and enemies are close, attac closest
        if archon.weapon_cooldown == 0 and enemyUnits.exists:
            enemyUnits = enemyUnits.sorted(lambda x: x.distance_to(archon))
            closestEnemy = enemyUnits[0]
            self.actions.append(archon.attack(closestEnemy))
            return  # continue for loop, dont execute any of the following
        # If no targets nearby, initiate attack command
        elif self.ArmyStatus == self.status['attacking']:
            if self.known_enemy_units.closer_than(12,archon):
                self.actions.append(archon.attack(self.find_AnyTarget(archon)))
            else:
                await self.unitRally(archon)
        elif self.ArmyStatus == self.status['defending']:
            self.actions.append(archon.attack(self.find_AnyTarget(archon)))


    async def observer_behaviour(self, observer):
        if self.ArmyStatus == self.status['rallying']:
            if observer.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(observer.move(self.RallyPoint[0]))
                return

        enemyThreatsClose = self.known_enemy_units.not_structure.closer_than(6, observer)
        if self.ArmyStatus == self.status['attacking'] or self.ArmyStatus == self.status['defending']:
            if self.units(STALKER).exists:
                if observer.distance_to(self.units(STALKER).closest_to(observer)) > 1:
                    self.actions.append(observer.move(self.units(STALKER).closest_to(observer)))
            elif self.units(IMMORTAL).exists:
                if observer.distance_to(self.units(IMMORTAL).closest_to(observer)) > 1:
                    self.actions.append(observer.move(self.units(IMMORTAL).closest_to(observer)))
            elif self.units(VOIDRAY).exists:
                if observer.distance_to(self.units(VOIDRAY).closest_to(observer)) > 1:
                    self.actions.append(observer.move(self.units(VOIDRAY).closest_to(observer)))
            else:
                self.actions.append(observer.move(self.units.not_structure.exclude_type(PROBE).closest_to(observer)))



    async def sentry_behaviour(self, sentry):
        if self.ArmyStatus == self.status['rallying']:
            if sentry.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(sentry.move(self.RallyPoint[0]))
                return

        enemyThreats = self.known_enemy_units.not_structure.exclude_type(self.enemyWorker).closer_than(10, sentry)
        enemyThreatsClose = self.known_enemy_units.not_structure.exclude_type([UnitTypeId.EGG, self.enemyWorker]).closer_than(6, sentry)
        enemyThreatsVeryClose = self.known_enemy_units.not_structure.closer_than(3, sentry)
        target = random.choice([self.units(STALKER), self.units(ADEPT), self.units(ZEALOT)])
        abilities = (await self.get_available_abilities(sentry))

        # Force Field here
        if AbilityId.FORCEFIELD_FORCEFIELD in abilities and enemyThreatsClose.amount > 6:
            enemyUnit = enemyThreats.sorted(lambda x: x.distance_to(sentry))
            force_field = await self.can_cast(sentry, AbilityId.FORCEFIELD_FORCEFIELD, enemyUnit[0].position)
            if force_field:
                closestEnemy = enemyUnit[0].position
                if closestEnemy:
                    self.actions.append(sentry(AbilityId.FORCEFIELD_FORCEFIELD, enemyUnit[0].position))
                    return
       #elif AbilityId.FORCEFIELD_CANCEL in abilities and enemyThreats.exists:

        # Guardian Shield
        if AbilityId.GUARDIANSHIELD_GUARDIANSHIELD in abilities and enemyThreats.amount > 5 and not sentry.has_buff(
                BuffId.GUARDIANSHIELD):
            self.actions.append(sentry(AbilityId.GUARDIANSHIELD_GUARDIANSHIELD))
            return

        # Hallucination for stalkr
        if target.exists and target.closest_to(sentry).name.lower() == 'stalker':
            if AbilityId.HALLUCINATION_STALKER in abilities and enemyThreats.amount > 5 and self.units(
                    STALKER).closer_than(6, sentry).amount > 6:
                self.actions.append(sentry(AbilityId.HALLUCINATION_STALKER))
                return
            # Hallucination for adept
        elif target.exists and target.closest_to(sentry).name.lower() == 'adept':
            if AbilityId.HALLUCINATION_ADEPT in abilities and enemyThreats.amount > 5 and self.units(
                    ADEPT).closer_than(6, sentry).amount > 6:
                self.actions.append(sentry(AbilityId.HALLUCINATION_ADEPT))
                return
            # Hallucination for stalkr
        elif target.exists and target.closest_to(sentry).name.lower() == 'zealot':
            if AbilityId.HALLUCINATION_ZEALOT in abilities and enemyThreats.amount > 5 and self.units(
                    ZEALOT).closer_than(6, sentry).amount > 6:
                self.actions.append(sentry(AbilityId.HALLUCINATION_ZEALOT))
                return

        if self.ArmyStatus == self.status['attacking'] or self.ArmyStatus == self.status['defending']:
            if target.exists and target.closest_to(sentry).name.lower() == 'stalker':
                if sentry.distance_to(target.closest_to(sentry)) > 1:
                    self.actions.append(sentry.move(self.units(STALKER).closest_to(sentry)))
                    return

            if enemyThreatsVeryClose.exists:
                retreatPoints = self.neighbors8(sentry.position, distance=2) | self.neighbors8(sentry.position,
                                                                                               distance=4)
                # filter points that are pathable by a reaper
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreatsVeryClose.closest_to(sentry)
                    retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(sentry))
                    # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                    self.actions.append(sentry.move(retreatPoint))
                    return  # continue for loop, don't execute any of the following

            if enemyThreatsClose.exists:
                self.actions.append(sentry.attack(self.find_AnyTarget(sentry)))
                return
            else:
                await self.unitRally(sentry)


    async def warpprismTransport_behaviour(self, warpprism):
        if warpprism.tag in self.taskForce:
            target = self.taskForceTarget
            abilities = await self.get_available_abilities(warpprism)

            if self.known_enemy_units.not_structure.exclude_type(self.enemyWorker).amount > 3:
                self.taskForceSignal = 2

            if self.diversionAttack == 0 and warpprism.distance_to(target) < 25:
                self.diversionAttack = 1

            # Add units close to the target to taskforce list, in order to pick up later
            if self.units.filter \
                (lambda x: x.name.lower() == 'zealot' or x.name.lower() == 'adept' or x.name.lower() == 'disruptor').closer_than(12, target) \
                            and len(self.taskForce) < 4 and AbilityId.LOAD_WARPPRISM in abilities:
                for unit in self.units.closer_than(12, target):
                    if unit.tag not in self.taskForce:
                        self.taskForce.append(unit.tag)
            # if taskforce is forming up
            if (AbilityId.LOAD_WARPPRISM in abilities and warpprism.distance_to(self.RallyPoint[0]) < 25):
                unit = 0
                if self.taskForce_type == self.forcetype['disruptor']:
                    unit = self.units(DISRUPTOR).closest_to(warpprism)
                elif self.taskForce_type == self.forcetype['gateway_units']:
                    if self.units(ADEPT).exists:
                        unit = self.units(ADEPT).closest_to(warpprism)
                    elif self.units(ZEALOT).exists:
                        unit = self.units(ZEALOT).closest_to(warpprism)
                if await self.can_cast(warpprism, AbilityId.LOAD_WARPPRISM, unit) and unit.distance_to(warpprism) < 6:
                    self.actions.append(warpprism(AbilityId.LOAD_WARPPRISM, unit))
                else:
                    self.actions.append(warpprism.move(unit.position))
            # if mission is complete or aborted, load taskforce to warp prism
            elif AbilityId.LOAD_WARPPRISM in abilities and warpprism.distance_to(target) < 15 and\
                self.taskForceSignal == 1:
                for unit_tag in self.taskForce:
                    if self.units.find_by_tag(unit_tag):
                        unit = self.units.by_tag(unit_tag)
                        if unit != warpprism and await self.can_cast(warpprism, AbilityId.LOAD_WARPPRISM, unit):
                            self.actions.append(warpprism(AbilityId.LOAD_WARPPRISM, unit))
                            self.taskForce.remove(unit.tag)
                    else:
                        self.taskForce.remove(unit_tag)
            # if warp prism is loaded and ready to leave for task
            elif AbilityId.LOAD_WARPPRISM not in abilities and \
                    warpprism.distance_to(target) > 10 and self.taskForceSignal == 0:
                self.actions.append(warpprism.move(target))
            # if mission is complete or aborted and taskforce is loaded in the warp prism
            elif self.taskForceSignal == 1 and len(self.taskForce) < 2 and warpprism.distance_to(target) < 25:
                self.actions.append(warpprism.move(self.RallyPoint[0]))
            # if warp prism has arrived to target or arrived to rallypoint, unload all
            if (warpprism.distance_to(target) < 8 and
                not self.known_enemy_units.not_structure.exclude_type(self.enemyWorker).closer_than(10, target) and
                    AbilityId.UNLOADALLAT_WARPPRISM in abilities and self.taskForceSignal == 0) \
                    or (warpprism.distance_to(self.RallyPoint[0]) < 10 and AbilityId.UNLOADALLAT_WARPPRISM in abilities and\
                        self.taskForceSignal == 1):
                self.actions.append(warpprism(AbilityId.UNLOADALLAT_WARPPRISM, warpprism.position))
                self.taskForceSignal = 0
                self.diversionAttack = 0

            if self.taskForceSignal == 2:
                self.actions.append(warpprism.move(self.RallyPoint[0]))
                self.diversionAttack = 0
                self.taskForce = []

            enemyThreats = self.known_enemy_units.filter(lambda x: x.can_attack_air).closer_than(10, warpprism)
            if enemyThreats.exists:
                retreatPoints = self.neighbors8(warpprism.position, distance=2) | self.neighbors8(warpprism.position, distance=4)
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreats.closest_to(warpprism)
                    retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(warpprism))
                    self.actions.append(warpprism.move(retreatPoint))
                    return  # continue for loop, don't execute any of the following



        else:
            if self.ArmyStatus == self.status['rallying']:
                if warpprism.distance_to(self.RallyPoint[0]) > 8:
                    self.actions.append(warpprism.move(self.RallyPoint[0]))
                    return

            enemyThreats = self.known_enemy_units.closer_than(12, warpprism)
            enemyThreatsClose = self.known_enemy_units.not_structure.closer_than(3, warpprism)
            abilities = await self.get_available_abilities(warpprism)

            # Phasing
            if AbilityId.MORPH_WARPPRISMPHASINGMODE in abilities and enemyThreats.amount > 6 and not enemyThreatsClose:
                self.actions.append(warpprism(AbilityId.MORPH_WARPPRISMPHASINGMODE))
                return

            elif not self.known_enemy_units.not_structure.exclude_type(self.enemyWorker).closer_than(10, warpprism) and \
                    AbilityId.UNLOADALLAT_WARPPRISM in abilities:
                self.actions.append(warpprism(AbilityId.UNLOADALLAT_WARPPRISM, warpprism.position))

            elif enemyThreatsClose.exists:
                retreatPoints = self.neighbors8(warpprism.position, distance=2) | self.neighbors8(warpprism.position,distance=4)

                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreatsClose.closest_to(warpprism)
                    retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(warpprism))
                    self.actions.append(warpprism.move(retreatPoint))
                    return  # continue for loop, don't execute any of the following


            if self.ArmyStatus == self.status['attacking'] or self.ArmyStatus == self.status['defending']:
                if self.known_enemy_structures.closer_than(8, warpprism) and not enemyThreatsClose:
                    self.actions.append(warpprism(AbilityId.MORPH_WARPPRISMPHASINGMODE))
                    return
                else:
                    await self.unitRally(warpprism)
            elif self.ArmyStatus == self.status['defending']:
                if not self.known_enemy_units.closer_than(10, warpprism) and self.known_enemy_units.exists:
                    self.actions.append(warpprism.move(self.known_enemy_units.closest_to(warpprism)))


    async def warpprismPhasing_behaviour(self, warpprism):
        if self.ArmyStatus == self.status['rallying']:
            if warpprism.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(warpprism(AbilityId.MORPH_WARPPRISMTRANSPORTMODE))
                return

        enemyThreatsClose = self.known_enemy_units.not_structure.exclude_type(self.enemyWorker).closer_than(3, warpprism)
        enemyThreatsFar = self.known_enemy_units.exclude_type(self.enemyWorker).closer_than(14,warpprism)
        abilities = await self.get_available_abilities(warpprism)

        if self.ArmyStatus == self.status['attacking'] or self.ArmyStatus == self.status['defending']:

            if self.known_enemy_units.closer_than(10, warpprism) and \
                    AbilityId.UNLOADALLAT_WARPPRISM in abilities:
                self.actions.append(warpprism(AbilityId.UNLOADALLAT_WARPPRISM, warpprism.position))

            if enemyThreatsClose.exists:
                self.actions.append(warpprism(AbilityId.MORPH_WARPPRISMTRANSPORTMODE))
                return  # continue for loop, don't execute any of the following
            elif enemyThreatsFar.amount < 1:
                self.actions.append(warpprism(AbilityId.MORPH_WARPPRISMTRANSPORTMODE))


    async def colossus_behaviour(self, colossus):
        if self.ArmyStatus == self.status['rallying']:
            if colossus.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(colossus.move(self.RallyPoint[0]))
                return

        enemyThreatsClose = self.known_enemy_units.not_structure.closer_than(6.5, colossus)
        # Lance range with extended lance upgrade, not implemented
#        enemyThreatsClose = self.known_enemy_units.closer_than(9, colossus)
        # Colossus micro if enemies close
        if enemyThreatsClose.exists:
            retreatPoints = self.neighbors8(colossus.position, distance=2) | self.neighbors8(colossus.position, distance=4)
            # filter points that are pathable by a reaper
            retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
            if retreatPoints:
                closestEnemy = enemyThreatsClose.closest_to(colossus)
                retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(colossus))
                # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                self.actions.append(colossus.move(retreatPoint))
                return # continue for loop, don't execute any of the following

        if self.ArmyStatus == self.status['attacking']:
            if self.known_enemy_units.closer_than(12,colossus):
                self.actions.append(colossus.attack(self.find_AnyTarget(colossus)))
            else:
                await self.unitRally(colossus)
        elif self.ArmyStatus == self.status['defending']:
            self.actions.append(colossus.attack(self.find_AnyTarget(colossus)))


    async def disruptor_behaviour(self, disruptor):

        if self.ArmyStatus == self.status['rallying']:
            if disruptor.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(disruptor.move(self.RallyPoint[0]))
                return

        abilities = (await self.get_available_abilities(disruptor))
        UnitsNovaRange = self.known_enemy_units.not_structure.exclude_type(
            [UnitTypeId.LARVA, UnitTypeId.EGG]).closer_than(8, disruptor)

        if UnitsNovaRange.amount > 3 and AbilityId.EFFECT_PURIFICATIONNOVA in abilities:
            UnitsNovaRange = UnitsNovaRange.sorted(lambda x: x.distance_to(disruptor), reverse=True)
            furthestEnemy = None
            for enemy in UnitsNovaRange:
                if await self.can_cast(disruptor, AbilityId.EFFECT_PURIFICATIONNOVA, enemy.position,
                                       cached_abilities_of_unit=abilities):
                    furthestEnemy = enemy
                    break
            if furthestEnemy:
                self.actions.append(disruptor(AbilityId.EFFECT_PURIFICATIONNOVA, furthestEnemy.position))
                return

        enemyThreatsClose = self.known_enemy_units.not_structure.closer_than(7, disruptor)
        # Micro if enemies exist
        if enemyThreatsClose.exists:
            retreatPoints = self.neighbors8(disruptor.position, distance=2) | self.neighbors8(disruptor.position,
                                                                                             distance=4)
            # filter points that are pathable by a reaper
            retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
            if retreatPoints:
                closestEnemy = enemyThreatsClose.closest_to(disruptor)
                retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(disruptor))
                # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                self.actions.append(disruptor.move(retreatPoint))
                return  # continue for loop, don't execute any of the following

#        elif self.known_enemy_structures.closer_than(9, disruptor) and not enemyThreatsClose.exists:
#            target = None
#            for unit in self.units.not_structure.exclude_type(PROBE):
#                if unit.distance_to(disruptor) < 10:
#                    target = unit
#                    break
#            if target and disruptor.distance_to(target) > 3:
#                self.actions.append(disruptor.move(target.position))
#                return

        elif self.ArmyStatus == self.status['attacking']:
            if not self.known_enemy_units.closer_than(12, disruptor) and self.known_enemy_units.exists:
                await self.unitRally(disruptor)
        elif self.ArmyStatus == self.status['defending']:
            if not self.known_enemy_units.closer_than(12, disruptor) and self.known_enemy_units.exists:
                self.actions.append(disruptor.move(self.known_enemy_units.closest_to(disruptor)))


    async def disruptor_nova(self, nova):
        UnitsNovaRange = self.known_enemy_units.not_structure.exclude_type(
            [UnitTypeId.LARVA, UnitTypeId.EGG]).closer_than(9, nova)

        if UnitsNovaRange.exists:
            UnitsNovaRange = UnitsNovaRange.sorted(lambda x: x.distance_to(nova), reverse=True)
            furthestEnemy = UnitsNovaRange[0]
            if furthestEnemy:
                self.actions.append(nova.move(furthestEnemy.position))
                return

    async def phoenix_behaviour(self, phoenix):
        if self.ArmyStatus == self.status['rallying']:
            if phoenix.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(phoenix.move(self.RallyPoint[0]))
                return

        phoenix_targets = ['immortal', 'disruptor',
                           'siegetank', 'siegetanksieged', 'cyclone',
                           'queen', 'hydralisk', 'ravager']

        abilities = (await self.get_available_abilities(phoenix))
        enemyThreats = self.known_enemy_units.filter(
            lambda x: x.can_attack_air).closer_than(4.5, phoenix)
        enemyUnits = self.known_enemy_units.flying.not_structure.closer_than(8, phoenix)
        priorityUnits = self.known_enemy_units.filter(lambda x: x.name.lower() in phoenix_targets).closer_than(7, phoenix)
        GravitonTargets = self.known_enemy_units.not_flying.not_structure.closer_than(6, phoenix)

        # Phoenix general attack
        if priorityUnits.exists and phoenix.energy > 50:
            Enemy = 0
            for enemy in priorityUnits:
                if self.GravitonSignal is None:
                    # Graviton beam
                    if AbilityId.GRAVITONBEAM_GRAVITONBEAM  in abilities:
                        if await self.can_cast(phoenix, AbilityId.GRAVITONBEAM_GRAVITONBEAM, enemy,
                                               cached_abilities_of_unit=abilities) and phoenix.distance_to(enemy.position) < 4:
                            Enemy = enemy
                            break
            if Enemy:
                if phoenix.distance_to(Enemy.position) > 4:
                    self.actions.append(phoenix.move(Enemy.position))
                else:
                    self.actions.append(phoenix(AbilityId.GRAVITONBEAM_GRAVITONBEAM, Enemy))
                    self.GravitonTarget = Enemy
                    self.GravitonSignal = self.time
                    return

        elif GravitonTargets.exists and phoenix.weapon_cooldown != 0 and phoenix.energy > 50:
            Enemy = 0
            for enemy in GravitonTargets:
                if self.GravitonSignal is None:
                    # Graviton beam
                    if AbilityId.GRAVITONBEAM_GRAVITONBEAM in abilities:
                        if await self.can_cast(phoenix, AbilityId.GRAVITONBEAM_GRAVITONBEAM, enemy,
                                               cached_abilities_of_unit=abilities) and phoenix.distance_to(
                            enemy.position) < 4:
                            Enemy = enemy
                            break
            if Enemy:
                if phoenix.distance_to(Enemy.position) > 4:
                    self.actions.append(phoenix.move(Enemy.position))
                else:
                    self.actions.append(phoenix(AbilityId.GRAVITONBEAM_GRAVITONBEAM, Enemy))
                    self.GravitonTarget = Enemy
                    self.GravitonSignal = self.time
                    return

        if self.GravitonSignal is not None and (self.time - self.GravitonSignal > 10 or self.GravitonTarget is None):
            self.GravitonSignal = None
            self.GravitonTarget = None

        if self.GravitonTarget is not None:
            self.actions.append(phoenix.attack(self.GravitonTarget))

        elif enemyUnits.exists:
            enemyUnits = enemyUnits.sorted(lambda x: x.distance_to(phoenix))
            closestEnemy = enemyUnits[0]
            self.actions.append(phoenix.attack(closestEnemy))
            return
        elif enemyThreats.exists:
                retreatPoints = self.neighbors8(phoenix.position, distance=2) | self.neighbors8(phoenix.position,
                                                                                                 distance=4)
                # filter points that are pathable by a reaper
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreats.closest_to(phoenix)
                    retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(phoenix))
                    # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                    self.actions.append(phoenix.move(retreatPoint))
                    return  # continue for loop, don't execute any of the following

        elif self.ArmyStatus == self.status['attacking']:
            if self.known_enemy_units.closer_than(12, phoenix):
                self.actions.append(phoenix.attack(self.find_AirTarget(phoenix)))
            else:
                await self.unitRally(phoenix)
        elif self.ArmyStatus == self.status['defending']:
            self.actions.append(phoenix.attack(self.find_AirTarget(phoenix)))


    async def voidray_behaviour(self, voidray):
        if self.ArmyStatus == self.status['rallying']:
            if voidray.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(voidray.move(self.RallyPoint[0]))
                return

        abilities = (await self.get_available_abilities(voidray))
        enemyThreatsClose = self.known_enemy_units.not_structure.exclude_type(UnitTypeId.EGG).filter(lambda x: x.can_attack_air).closer_than(4, voidray)
        enemyUnits = self.known_enemy_units.not_structure.exclude_type(UnitTypeId.EGG).closer_than(6, voidray)

        voidray_targets = ['immortal', 'clolossus', 'voidray', 'carrier', 'mothership', 'tempest', 'oracle', 'disruptor',
                           'siegetank', 'siegetanksieged', 'thor', 'viking', 'medivac', 'battlecruiser', 'autoturret', 'cyclone', 'liberator',
                           'ultralisk', 'corruptor', 'broodlord']

        # If health is under 4/10 then retreat behind lines and regen Shield (doesnt work on ramps, crashes)
        if voidray.health_percentage < 4 / 10 and voidray.shield_percentage == 0 and enemyThreatsClose.exists:
            retreatPoints = self.neighbors8(voidray.position, distance=2) | self.neighbors8(voidray.position,
                                                                                            distance=4)
            # filter points that are pathable
            retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
            # magicu, copied from terran example
            try:
                if retreatPoints:
                    closestEnemy = enemyThreatsClose.closest_to(voidray)
                    retreatPoint = closestEnemy.position.furthest(retreatPoints)
                    self.actions.append(voidray.move(retreatPoint))
                    return  # continue for loop, dont execute any of the following
            except:
                # in furthest
                #     return ps[0]
                # TypeError: 'set' object does not support indexing
                # I will fix later, ok?
                return

        # Voidray micro if enemies close
#        if enemyThreatsClose.exists:
#            retreatPoints = self.neighbors8(voidray.position, distance=2) | self.neighbors8(voidray.position,
#                                                                                             distance=4)
            # filter points that are pathable by a reaper
#            retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
#            if retreatPoints:
#                closestEnemy = enemyThreatsClose.closest_to(voidray)
#                retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(voidray))
                # retreatPoint = closestEnemy.position.furthest(retreatPoints)
#                self.actions.append(voidray.move(retreatPoint))
#                return  # continue for loop, don't execute any of the following

        # Voidray general attack
        if enemyUnits.exists:
            # If there are enemy flying units backing up troops
            enemyFlyingUnits = self.known_enemy_units.not_structure.flying.closer_than(8, voidray)
            voidrayPriorityTarget = 0

            for enemy in self.known_enemy_units.not_structure.closer_than(9, voidray):
                if enemy.name.lower() in voidray_targets:
                    voidrayPriorityTarget = 1

            if voidrayPriorityTarget:
                # Prismatic Alignment
                if AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT in abilities:
                    self.actions.append(voidray(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT))

                enemyUnits = [x for x in self.known_enemy_units.not_structure.closer_than(12, voidray) if
                              x.name.lower() in voidray_targets]
                enemyUnits.sort(key=lambda x: x.distance_to(voidray))

            elif enemyFlyingUnits.exists:
                enemyUnits = enemyFlyingUnits.sorted(lambda x: x.distance_to(voidray))
            else:
                enemyUnits = enemyUnits.sorted(lambda x: x.distance_to(voidray))
            closestEnemy = enemyUnits[0]
            self.actions.append(voidray.attack(closestEnemy))
        elif self.ArmyStatus == self.status['attacking']:
            if self.known_enemy_units.closer_than(12, voidray):
                self.actions.append(voidray.attack(self.find_AnyTarget_AirPriority(voidray)))
            else:
                await self.unitRally(voidray)
        elif self.ArmyStatus == self.status['defending']:
            self.actions.append(voidray.attack(self.find_AnyTarget_AirPriority(voidray)))


    async def tempest_behaviour(self, tempest):

        if self.ArmyStatus == self.status['rallying']:
            if tempest.distance_to(self.RallyPoint[0]) > 8:
                self.actions.append(tempest.move(self.RallyPoint[0]))
                return

        enemyThreatsClose = self.known_enemy_units.not_structure.exclude_type(UnitTypeId.EGG).filter(lambda x: x.can_attack_air).closer_than(9.5, tempest)
        enemyUnits = self.known_enemy_units.not_structure.exclude_type(UnitTypeId.EGG).closer_than(10, tempest)

        tempest_targets = ['thor', 'battlecruiser',
                           'ultralisk', 'broodlord',
                           'archon', 'colossus', 'carrier', 'mothership']

        # Tempest micro if enemies close
        if enemyThreatsClose.exists and tempest.weapon_cooldown != 0:

            retreatPoints = self.neighbors8(tempest.position, distance=2) | self.neighbors8(tempest.position,
                                                                                             distance=4)
            # filter points that are pathable by a tempest
            retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
            if retreatPoints:
                closestEnemy = enemyThreatsClose.closest_to(tempest)
                retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(tempest))
                # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                self.actions.append(tempest.move(retreatPoint))
                return  # continue for loop, don't execute any of the following

        # Tempest general attack
        if tempest.weapon_cooldown == 0 and enemyUnits.exists:
            # If there are enemy flying units backing up troops
            enemyFlyingUnits = self.known_enemy_units.not_structure.flying.closer_than(12, tempest)

            tempestPriorityTarget = 0
            for enemy in self.known_enemy_units.not_structure.closer_than(12, tempest):
                if enemy.name.lower() in tempest_targets:
                    tempestPriorityTarget = 1

            if tempestPriorityTarget:
                enemyUnits = [x for x in self.known_enemy_units.not_structure.closer_than(12, tempest) if
                                  x.name.lower() in tempest_targets]
                enemyUnits.sort(key=lambda x: x.distance_to(tempest))
            elif enemyFlyingUnits.exists:
                enemyUnits = enemyFlyingUnits.sorted(lambda x: x.distance_to(tempest))
            else:
                enemyUnits = enemyUnits.sorted(lambda x: x.distance_to(tempest))
            closestEnemy = enemyUnits[0]
            self.actions.append(tempest.attack(closestEnemy))
            return
        elif self.ArmyStatus == self.status['attacking']:
            if self.known_enemy_units.closer_than(12, tempest):
                self.actions.append(tempest.attack(self.find_AnyTarget_AirPriority(tempest)))
            else:
                await self.unitRally(tempest)
        elif self.ArmyStatus == self.status['defending']:
            self.actions.append(tempest.attack(self.find_AnyTarget_AirPriority(tempest)))



    # this checks if a ground unit can walk on a Point2 position
    def inPathingGrid(self, pos):
        # returns True if it is possible for a ground unit to move to pos - doesnt seem to work on ramps or near edges
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self._game_info.pathing_grid[(pos)] != 0


    # stolen and modified from position.py
    def neighbors4(self, position, distance=1):
        p = position
        d = distance
        return {
            Point2((p.x - d, p.y)),
            Point2((p.x + d, p.y)),
            Point2((p.x, p.y - d)),
            Point2((p.x, p.y + d)),
        }

    # stolen and modified from position.py
    def neighbors8(self, position, distance=1):
        p = position
        d = distance
        return self.neighbors4(position, distance) | {
            Point2((p.x - d, p.y - d)),
            Point2((p.x - d, p.y + d)),
            Point2((p.x + d, p.y - d)),
            Point2((p.x + d, p.y + d)),
        }


    def random_location_variance(self, enemy_start_location):
        x = enemy_start_location[0]
        y = enemy_start_location[1]

        x += ((random.randrange(-20, 20))/100) * enemy_start_location[0]
        y += ((random.randrange(-20, 20))/100) * enemy_start_location[1]

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > self.game_info.map_size[0]:
            x = self.game_info.map_size[0]
        if y > self.game_info.map_size[1]:
            y = self.game_info.map_size[1]

        go_to = position.Point2(position.Pointlike((x,y)))
        return go_to


#    async def _issue_unit_added_events(self):
#        for unit in self.units.not_structure:
#            if unit.tag not in self._units_previous_map:
#                await self.on_unit_created(unit)
#                print (unit)

#    async def _issue_unit_dead_events(self):
#        event = self.state.observation.raw_data.event
#        if event is not None:
#            for tag in event.dead_units:
#                await self.on_unit_destroyed(tag)

#    async def on_unit_created(self, unit: Unit):
#        if Unit == self.units.not_structure.exclude_type(PROBE):
#            self.army_list.append(Unit)
#            print (self.army_list)

#    async def on_unit_destroyed(self, unit_tag):
#        for a in self.army_list:
#            if a['tag'] == unit_tag:
#                self.army_list.remove(a)