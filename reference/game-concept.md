# Game concept

This note describes the original design direction for Better Together. It is a concept document, not a promise that every detail already exists in the current prototype.

## High-level pitch

Better Together is a four-player cooperative multiplayer game about organization under pressure. Players share a single fragile situation, face more work than they can comfortably handle alone, and must constantly decide what matters most right now.

The core fantasy is not just “doing tasks” — it is coordinating as a crew, reacting to emergencies, covering for each other, and recovering from mistakes before the match spirals out of control.

## Core design pillars

- **Shared pressure:** the whole team suffers when important work is ignored.
- **Prioritization over perfection:** players cannot do everything at once, so choosing the next task is the real game.
- **Cooperation creates efficiency:** helping another player on a critical task can be stronger than splitting up.
- **Escalation over time:** new task types and higher urgency appear as the match continues.
- **Readable chaos:** the situation should feel intense, but players should still be able to understand why they are winning or losing.

## Match structure

- A match starts with up to four player slots.
- The crew shares one environment and one overall loss state.
- Every player is free to move, react, and change focus as the match evolves.
- Victory comes from surviving long enough to reach the end-of-match timer.
- Defeat comes from poor organization, ignored urgent problems, or repeated bad prioritization that overwhelms the crew.

## Intended gameplay loop

The intended loop is a repeating cycle of observation, prioritization, execution, and recovery:

1. **Read the current state.**
	Players quickly scan the environment: which systems are stable, which tasks are building up, and which problems are becoming dangerous.
2. **Call priorities.**
	The team decides what must be handled immediately, what can wait, and whether players should group up or spread out.
3. **Commit to short jobs.**
	Players move to objectives and perform focused task loops such as repairing damage, reloading, defending, transporting resources, or stabilizing a failing part of the ship.
4. **React to interruptions.**
	New threats appear while old ones are still being solved. A player may need to abandon a low-priority task to help with a critical emergency.
5. **Rebalance the crew.**
	Once an urgent task is under control, players redistribute again instead of staying locked to one role forever.
6. **Survive the next wave of pressure.**
	The game continues to introduce new complications, forcing the team to repeat the loop under tighter timing and higher stakes.

The important part is that the loop should create meaningful trade-offs:

- help another player finish a critical task faster, or start a separate task alone;
- protect the ship now, or prepare for the next incoming problem;
- spend time recovering from damage, or maintain offensive pressure;
- handle the visible problem, or intercept the hidden problem that will become urgent in a few seconds.

## Task structure

Tasks should not all feel the same. The match becomes more interesting when objectives fall into different categories:

- **Immediate emergencies** — problems that can directly cause defeat if ignored.
- **Maintenance tasks** — recurring work that prevents the situation from degrading.
- **Support tasks** — preparation work that makes future emergencies easier to solve.
- **Opportunity tasks** — actions that buy time, restore resources, or reduce future pressure.

As the match goes on, new task types should appear and combine in ways that stress coordination. The goal is to create moments where the team has several valid options, but only one or two are truly smart.

## Cooperation model

Players should regularly face decisions like:

- stay together to complete one urgent task quickly;
- split up to stop multiple smaller problems from stacking;
- cover for a weaker or overloaded teammate;
- rotate responsibilities because the current assignment is no longer efficient.

Cooperation should feel active rather than passive. Players are not just standing near each other — they are intentionally increasing each other’s effectiveness by timing, positioning, and task choice.

## Pressure and escalation

The match should become harder over time in a way that is easy to feel:

- urgent events arrive more often,
- recovery windows become shorter,
- unattended tasks create follow-up problems,
- and mistakes are harder to fully erase once the match is in a bad state.

This escalation is what turns basic task execution into a coordination game. A calm early match teaches the systems; a late match tests whether the crew can still prioritize correctly under stress.

## Failure and victory

- **Victory:** survive until the match timer expires.
- **Failure:** let the team state collapse because urgent tasks were ignored, delayed, or consistently solved in the wrong order.

The failure state should feel fair: players should be able to look back and understand which priorities were missed and where coordination broke down.

## Multiplayer continuity

A match starts with four player slots. If one player disconnects, the computer takes over that slot until another player joins.

The AI replacement can scale in strength depending on how many human players are currently connected:

- stronger when the number of humans is low,
- weaker when the crew is already close to full,
- and always focused on keeping the match playable rather than outperforming coordinated humans.

If a match no longer has any AI-controlled slot available, a newly connecting player should create or join another match in parallel instead of being blocked from play. This keeps the game ready for future players without disturbing a full human crew.

## Intended player experience

At its best, a match should feel like this:

- the team barely holds things together,
- someone notices the next big problem just in time,
- two players combine on a critical task while the others buy them space,
- the situation stabilizes for a moment,
- and then a new wave of pressure forces everyone to reprioritize again.

That rhythm of **panic, coordination, recovery, and renewed pressure** is the heart of the concept.
