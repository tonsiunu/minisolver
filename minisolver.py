# MiniSolver event feed parser
# Change every line marked with TODO to match the details for this contest

import json
from time import sleep
from enum import *

class ProblemState(Enum):
    UNSOLVED = 0
    AC = 1
    WA = 2
    FROZEN_AC = 3
    FROZEN_WA = 4

# make sure these are in order of the contest!
problem_ids = [561, 562, 563, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578] # TODO every problem's ID on DOMjudge
problem_scores = [6, 6, 1, 7, 9, 6, 4, 3, 6, 3, 3, 10, 11, 11, 14] # TODO every problem's score
test_cases = [7, 11, 21, 11, 11, 14, 70, 70, 11, 11, 11, 22, 10, 29, 49] # TODO every problem's number of test case files

freeze_time = 90 # TODO time of the freeze in minutes
contest_length = 180 # TODO contest length in minutes (hopefully you shouldn't have to change this)

# all three of these IDs should be STRINGS
inperson_id = "18" # TODO replace with the group ID of In-Person teams, or empty string if there aren't any
online_id = "17" # TODO replace with the group ID of Online teams
asdan_id = "19" # TODO replace with the group ID of ASDAN teams, or empty string if there aren't any

assert sum(problem_scores) == 100, sum(problem_scores)
assert len(test_cases) == len(problem_scores)

class Team:
    def __init__(self, json, is_college):
        self.id = json["id"]
        self.name = json["name"]
        self.is_inperson = int(inperson_id in json["group_ids"])
        self.is_college = int(is_college)
        self.problems = [ProblemState.UNSOLVED] * len(problem_scores)
        self.penalties = [0] * len(problem_scores)
        self.seen_judgements = {}

    def update_problem(self, problem, state, judgement, no_pen=False, minutes=0):
        if judgement in self.seen_judgements and self.seen_judgements[judgement] == state: # do nothing if already seen this judging
            return
        if self.problems[problem].value % 2 == 1: # do nothing if team already has an AC submission
            return
        self.problems[problem] = state
        if state.value % 2 == 1:
            self.penalties[problem] += minutes
            if judgement in self.seen_judgements and self.seen_judgements[judgement].value % 2 == 0: # that annoying edge case of judgements firing no output
                self.penalties[problem] -= 10
        elif not no_pen: # only add penalty if code compiled
            self.penalties[problem] += 10

        self.seen_judgements[judgement] = state

    def score(self):
        score = 0
        for i in range(len(problem_scores)):
            if self.problems[i].value == 1:
                score += problem_scores[i]
        return score
    
    def penalty_time(self):
        pen = 0
        for i in range(len(problem_scores)):
            if self.problems[i].value == 1:
                pen += self.penalties[i]
        return pen
    
    def resolve_next(self):
        for i in range(len(problem_scores)):
            if self.problems[i].value > 2:
                print("Now Resolving team", self.name, "with problem", i)
                sleep(0.1)
                if self.problems[i].value == 3:
                    self.problems[i] = ProblemState.AC
                    print("Result: YES")
                    return "YES"
                else:
                    self.problems[i] = ProblemState.WA
                    print("Result: NO")
                    return "NO"
                        
        return "DONE"

    def __repr__(self):
        return self.name
    
# begin pre-processing

all_teams = {}
mega_file = open("event-feed.json").read().splitlines()
college_teams = open("college-teams.txt").read().splitlines()
pending_submissions = {}
pending_judgements = {}

for l in mega_file:
    data = json.loads(l)
    if data["type"] == "teams" and data["data"]["group_ids"][0] in [inperson_id, online_id, asdan_id]:
        all_teams[data["data"]["id"]] = Team(data["data"], data["data"]["name"] in college_teams)

    if data["type"] == "submissions" and data["data"]["team_id"] in all_teams:
        problem = problem_ids.index(int(data["data"]["problem_id"]))
        time = data["data"]["contest_time"].split(":")
        minutes = int(time[0]) * 60 + int(time[1])
        if 0 <= minutes < contest_length:
            pending_submissions[data["data"]["id"]] = [problem, minutes, data["data"]["team_id"]] # problem id, minutes elapsed, team id
      
    if data["type"] == "judgements" and data["data"]["submission_id"] in pending_submissions and not data["data"]["judgement_type_id"]:
        sub = pending_submissions[data["data"]["submission_id"]]
        pending_judgements[data["data"]["id"]] = sub + ["CE", test_cases[sub[0]]] # problem id, minutes elapsed, team id, most recent verdict, number of ACs expected

    if data["type"] == "judgements" and data["data"]["submission_id"] in pending_submissions and data["data"]["judgement_type_id"]:
        sub = pending_submissions[data["data"]["submission_id"]]
        if data["data"]["id"] not in pending_judgements:
            pending_judgements[data["data"]["id"]] = sub + ["CE", test_cases[sub[0]]] # problem id, minutes elapsed, team id, most recent verdict, number of ACs expected
        else:
            del pending_judgements[data["data"]["id"]]

        if data["data"]["judgement_type_id"] == "AC":
            if sub[1] >= freeze_time:
                all_teams[sub[2]].update_problem(sub[0], ProblemState.FROZEN_AC, data["data"]["id"], True, sub[1])
            else:
                all_teams[sub[2]].update_problem(sub[0], ProblemState.AC, data["data"]["id"], True, sub[1])
        else:
            no_pen = data["data"]["judgement_type_id"] == "CE" # only add penalty if code compiled
            if sub[1] >= freeze_time:
                all_teams[sub[2]].update_problem(sub[0], ProblemState.FROZEN_WA, data["data"]["id"], no_pen)
            else:
                all_teams[sub[2]].update_problem(sub[0], ProblemState.WA, data["data"]["id"], no_pen)
                    

# clean up the missing judgings

for l in mega_file:
    data = json.loads(l)
    if data["type"] == "runs" and data["data"]["judgement_id"] in pending_judgements:
        pending_judgements[data["data"]["judgement_id"]][3] = data["data"]["judgement_type_id"]
        if data["data"]["judgement_type_id"] == "AC":
            pending_judgements[data["data"]["judgement_id"]][4] -= 1
    
for j, judging in pending_judgements.items():
    if judging[3] == "AC" and judging[4] == 0: # need enough ACs
        if judging[1] >= freeze_time:
            all_teams[judging[2]].update_problem(judging[0], ProblemState.FROZEN_AC, j, True, judging[1])
        else:
            all_teams[judging[2]].update_problem(judging[0], ProblemState.AC, j, True, judging[1])
    elif judging[3] != "AC":
        no_pen = judging[3] == "CE" # only add penalty if code compiled
        if judging[1] >= freeze_time:
            all_teams[judging[2]].update_problem(judging[0], ProblemState.FROZEN_WA, j, no_pen)
        else:
            all_teams[judging[2]].update_problem(judging[0], ProblemState.WA, j, no_pen)

# end pre-processing

# generate csv file for web version

output = []
for k, v in all_teams.items():
    line = []
    line.append(str(v.is_college))
    line.append(str(v.is_inperson))
    line.extend([str(x.value) for x in v.problems])
    line.extend([str(x) for x in v.penalties])
    line.append(v.name)
    output.append(line)

output.sort(key=lambda x: x[-1])

f = open("resolver-output.txt", "w", encoding="utf-8")
f.write("\n".join([",".join(x) for x in output]))
f.close()

num_teams_entered = len([x for x in all_teams.values() if sum(x.penalties) > 0])
print(num_teams_entered, "Teams Competed")

gold_threshold = num_teams_entered // 12
silver_threshold = num_teams_entered // 6 - gold_threshold
bronze_threshold = num_teams_entered // 3 - silver_threshold - gold_threshold

print("Gold Teams:", gold_threshold)
print("Silver Teams:", silver_threshold)
print("Bronze Teams:", bronze_threshold)

# text-based version of resolver starts here

sleep(5)

# pre-freeze leaderboard

leaderboard = []
for k, v in all_teams.items():
    leaderboard.append(v)

leaderboard.sort(key=lambda x: x.name)
leaderboard.sort(key=lambda x: x.penalty_time())
leaderboard.sort(key=lambda x: x.score(), reverse=True)

place = len(leaderboard) - 1

# resolution

while place >= 0:
    curr_team = leaderboard[place]
    answer = "NO"
    while answer == "NO":    
        answer = curr_team.resolve_next()
        sleep(0.1)

    if answer == "YES":
        leaderboard.sort(key=lambda x: x.name)
        leaderboard.sort(key=lambda x: x.penalty_time())
        leaderboard.sort(key=lambda x: x.score(), reverse=True)

    if answer == "DONE":
        print("Team", curr_team.name, "ends in place", place + 1)
        sleep(0.1)
        place -= 1
