# MiniSolver
MiniSolver is made with love by tonsi

## Setup
During (or even before) the contest, update the **minisolver.py** script and the **index.html** webpage by changing every line marked with TODO to match the details for the current contest. All the information should be available on DOMjudge without the contest having begun.

Once the contest is over, before running the resolver, you'll need to get the event feed. This should be done using the standard ICPC resolver (TODO add link), with the following steps:
1. Make sure you're logged into DOMjudge as admin.
2. Go to https://calicojudge.com/jury/contests/ and find the ID number for the current contest.
3. Open a terminal and navigate to the folder where you downloaded the ICPC resolver, then run the awards script (awards.bat on Windows, awards.sh on Mac/Linux).
4. Click the REST tab in the window that pops up.
5. Fill out the credentials of the DOMjudge admin account, and in URL write https://calicojudge.com/api/contests/CONTEST-ID/
6. You should get a window with a list of all the teams, don't worry about anything else on screen, just hit Save and name the file **event-feed.json**
7. Put this file in the same folder as minisolver.py, and run it. You should get a new text file called **resolver-output.txt**; now you can run the site!

To run the resolver, just open index.html in your browser.

## Leaderboard
Every row of the leaderboard while in resolution contains the team's rank, name, score, and a list of cells for each problem in the contest. The colors of the cells indicate the status:
* Grey: no attempt
* Red: incorrect
* Green: correct
* Amber: still to be resolved
* Blue: submission queued

The scores and penalty times listed do not include problems that are still to be resolved. They will increase as resolutions are completed.

## Control
The key to advancing in the site (pun intended) is to **just press space**. If you're ever stuck, give it a press.

Once you click the Start button, the first event will be to honor all the teams that achieved a Bronze placing. There is no live resolution; only their name and score will show. The names will fill the table automatically; once it's full, press space to generate more names.

Once all the Bronze teams have been honored, the resolver stage will begin, featuring all Silver and Gold teams. This is the heart of it all.

The following is what you can expect with each space press during the resolver stage:
* While the leaderboard is in the idle state (i.e. no rows highlighted), on a space press, the team at the bottom place still to be resolved will have their row highlighted.
* On the next space press, the highlighted team's next pending submission will be queued up by changing the corresponding cell color from amber to blue. This will allow you to create a bit of suspense.
* On the next space press, if the submission is incorrect, then the cell will turn red. Pressing again will queue up the team's next pending submission. If a submission is correct, then the cell will turn green and the leaderboard will be re-sorted to reflect the team's score increasing. The leaderboard is now in the idle state again.
* If the highlighted team has no more pending submissions, then a space press will cause the highlight to be removed and the leaderboard to move up one place. The leaderboard is now in the idle state again. However, if this team is in a special placing, then the next space press after this step will show a special screen congratulating the team. Pressing again after that will return to the leaderboard.

If there are ever any issues, then feel free to ping me @tonsi.mu in the CALICO Team server. No guarantee I'll be awake during the contest depending on where I am in the world, but I'll do my best.