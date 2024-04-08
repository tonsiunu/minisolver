import json
from enum import *

class ProblemState(Enum):
    UNSOLVED = 0
    AC = 1
    WA = 2
    FROZEN_AC = 3
    FROZEN_WA = 4

problem_scores = [3, 3, 2, 3, 4, 4, 1, 4, 2, 3, 5, 4, 2, 2, 6, 2, 2, 1, 7, 4, 7, 3, 12, 1, 13]
assert sum(problem_scores) == 100

class Team:
    def __init__(self, json):
        self.id = json["id"]
        self.name = json["name"]
        # TODO pre-college check
        self.problems = [ProblemState.UNSOLVED] * 25
        self.penalties = [0] * 25

    def update_problem(self, problem, state, no_pen=False, minutes=0):
        if self.problems[problem].value % 2 == 1: # do nothing if team already has an AC submission
            return
        self.problems[problem] = state
        if state.value % 2 == 1:
            self.penalties[problem] += minutes
        elif not no_pen: # only add penalty if code compiled
            self.penalties[problem] += 10

    def score(self, post_freeze=True):
        score = 0
        for i in range(25):
            if self.problems[i].value == 1 or (self.problems[i].value == 3 and post_freeze):
                score += problem_scores[i]
        return score
    
    def penalty_time(self, post_freeze=True):
        pen = 0
        for i in range(25):
            if self.problems[i].value == 1 or (self.problems[i].value == 3 and post_freeze):
                pen += self.penalties[i]
        return pen

    def __repr__(self):
        return self.name

all_teams = {}
mega_file = open("new-event-feed.ndjson").read().splitlines()
pending_submissions = {}

for l in mega_file:
    data = json.loads(l)
    if data["type"] == "teams" and data["data"]["group_ids"][0] in ["15", "16"]:
        all_teams[data["data"]["id"]] = Team(data["data"])

    if data["type"] == "submissions" and data["data"]["team_id"] in all_teams:
        problem = int(data["data"]["problem_id"]) - 495
        time = data["data"]["contest_time"].split(":")
        minutes = int(time[0]) * 60 + int(time[1])
        pending_submissions[data["data"]["id"]] = (problem, minutes, data["data"]["team_id"])

    if data["type"] == "judgements" and data["data"]["submission_id"] in pending_submissions and data["data"]["judgement_type_id"]:
        sub = pending_submissions[data["data"]["submission_id"]]

        if data["data"]["judgement_type_id"] == "AC":
            if sub[1] >= 150:
                all_teams[sub[2]].update_problem(sub[0], ProblemState.FROZEN_AC, True, sub[1])
            else:
                all_teams[sub[2]].update_problem(sub[0], ProblemState.AC, True, sub[1])
        else:
            no_pen = data["data"]["judgement_type_id"] == "CE" # only add penalty if code compiled
            if sub[1] >= 150:
                all_teams[sub[2]].update_problem(sub[0], ProblemState.FROZEN_WA, no_pen)
            else:
                all_teams[sub[2]].update_problem(sub[0], ProblemState.WA, no_pen)
                    
