import random
from collections import defaultdict
import itertools

# --- YOUR FANTASY FOOTBALL DATA ---
teams = ['Ross', 'Logan', 'Matt', 'Eric', 'Graeme', 'Danny', 'Kurt', 'Austin', 'Thomas', 'Nick']

# Define the pairs of teams that will play each other twice
# The order within the tuple doesn't matter (e.g., ('Jake', 'Sum') is same as ('Sum', 'Jake'))
double_play_pairs = [
    ('Logan', 'Matt'), ('Logan', 'Eric'), ('Logan', 'Graeme'), ('Logan', 'Danny'), ('Matt', 'Eric'),
    ('Matt', 'Graeme'), ('Matt', 'Danny'), ('Eric', 'Graeme'), ('Eric', 'Danny'), ('Graeme', 'Danny'),
    ('Kurt', 'Austin'), ('Kurt', 'Thomas'), ('Kurt', 'Nick'), ('Kurt', 'Ross'), ('Austin', 'Thomas'),
    ('Austin', 'Nick'), ('Austin', 'Ross'), ('Thomas', 'Nick'), ('Thomas', 'Ross'), ('Nick', 'Ross'),

    ('Danny', 'Ross'), ('Graeme', 'Nick'), ('Matt', 'Thomas'), ('Eric', 'Austin'), ('Logan', 'Kurt')
]

# Define the specific matchups for designated weeksa
# Week number as key, list of (TeamA, TeamB) tuples as value
fixed_matchups = {
    4: [('Ross', 'Eric'), ('Danny', 'Kurt'), ('Matt', 'Logan'), ('Graeme', 'Austin'), ('Thomas', 'Nick')]
}

# Define constants for the schedule
num_weeks = 14
MIN_WEEKS_BETWEEN_REPEAT = 3  # Minimum number of weeks between playing the same opponent
max_attempts = 50000  # Limit the number of attempts to find a schedule

def generate_fantasy_schedule():
    # Convert double_play_pairs_input to frozensets for consistent lookup
    # frozenset allows us to treat ('A', 'B') and ('B', 'A') as the same pair
    double_play_pairs_fs = {frozenset(pair) for pair in double_play_pairs}

    # Initialize schedule for all weeks
    schedule = {w: [] for w in range(1, num_weeks + 1)}

    # Track how many games each pair still needs to play
    # Default to 0 for pairs not yet considered
    remaining_games_needed = defaultdict(int)
    all_possible_pairs = set()

    # Track the last week each pair played
    last_played_week = defaultdict(int)

    # Populate all possible pairs and set their target game counts (1 or 2)
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            pair = frozenset({teams[i], teams[j]})
            all_possible_pairs.add(pair)
            if pair in double_play_pairs_fs:
                remaining_games_needed[pair] = 2
            else:
                remaining_games_needed[pair] = 1

    # Apply fixed matchups and update remaining game counts and last played week
    fixed_weeks = set()
    for w, match in fixed_matchups.items():
        fixed_weeks.add(w)
        for m in match:
            t1, t2 = m[0], m[1]
            pair = frozenset({t1, t2})

            if pair not in all_possible_pairs:
                print(f"Error: Fixed matchup {tuple(m)} is not a valid pair of teams. Please check team names.")
                return None
            if remaining_games_needed[pair] <= 0:
                print(
                    f"Error: Fixed matchup {tuple(m)} scheduled more times than allowed. Week {w}. Review double-play settings.")
                return None
            if last_played_week[pair] > 0 and w - last_played_week[
                pair] < 1:  # Check for immediate back-to-back in fixed
                print(
                    f"Error: Fixed matchup {tuple(m)} is scheduled back-to-back in Week {w} and Week {last_played_week[pair]}. Please adjust fixed matchups.")
                return None

            # Store matchups as sorted tuples for consistent output (e.g., ('Jake', 'Sum'))
            schedule[w].append(tuple(sorted(list(pair))))
            remaining_games_needed[pair] -= 1
            last_played_week[pair] = w  # Record the week this pair played

    attempt_count = 0

    while attempt_count < max_attempts:
        # Create fresh copies for each attempt
        current_remaining_games = remaining_games_needed.copy()
        current_schedule = {w: list(schedule[w]) for w in range(1, num_weeks + 1)}
        current_last_played_week = last_played_week.copy()  # Copy last played week tracking

        try:
            for w in range(1, num_weeks + 1):
                if w in fixed_weeks:
                    continue  # Skip weeks that are already fixed

                # Get teams that have already been assigned a game this week from fixed matchups (if any)
                teams_assigned_this_week = set()
                for m in current_schedule[w]:
                    teams_assigned_this_week.add(m[0])
                    teams_assigned_this_week.add(m[1])

                # Get teams that are still available to be assigned a game this week
                teams_available_this_week_for_new_games = set(teams) - teams_assigned_this_week

                # List potential matchups that still need to be played and involve available teams
                potential_matchups_for_this_week = []
                for p in all_possible_pairs:
                    if current_remaining_games[p] > 0:
                        t1, t2 = list(p)
                        # Check if both teams are available and meet the minimum weeks between repeat constraint
                        if t1 in teams_available_this_week_for_new_games and t2 in teams_available_this_week_for_new_games:
                            # Check the minimum weeks between repeat constraint
                            if w - current_last_played_week[p] >= MIN_WEEKS_BETWEEN_REPEAT or \
                                    current_last_played_week[p] == 0:
                                # Prioritize double-play pairs that still need their second game
                                if p in double_play_pairs_fs and current_remaining_games[p] == 2:
                                    potential_matchups_for_this_week.insert(0, p)  # Higher priority for second game
                                else:
                                    potential_matchups_for_this_week.append(p)

                random.shuffle(potential_matchups_for_this_week)  # Randomize to explore different combinations

                week_matchups_to_add = []
                teams_assigned_this_week_in_loop = set()  # To track teams assigned during this week's filling process

                for match in potential_matchups_for_this_week:
                    t1, t2 = list(match)
                    # Check if both teams are available for this week
                    if t1 not in teams_assigned_this_week_in_loop and t2 not in teams_assigned_this_week_in_loop:
                        week_matchups_to_add.append(tuple(sorted(list(match))))
                        teams_assigned_this_week_in_loop.add(t1)
                        teams_assigned_this_week_in_loop.add(t2)
                        current_remaining_games[match] -= 1
                        current_last_played_week[match] = w  # Update last played week

                        if len(week_matchups_to_add) + len(
                                current_schedule[w]) == len(teams) // 2:  # All games filled for the week
                            break

                # If we couldn't fill all slots for the week, this attempt failed
                if len(week_matchups_to_add) + len(current_schedule[w]) != len(teams) // 2:
                    raise ValueError(f"Could not fill Week {w} with available matchups. Retrying.")

                current_schedule[w].extend(week_matchups_to_add)

            # If we reach here, a schedule has been constructed. Now, verify all games were played.
            if all(count == 0 for count in current_remaining_games.values()):
                print(f"Schedule found after {attempt_count + 1} attempts!")
                return current_schedule
            else:
                raise ValueError("Not all games played as required. Retrying.")


        except ValueError as e:
            # print(f"Attempt failed: {e}") # Uncomment for debugging attempts
            pass  # Continue to the next attempt

        attempt_count += 1

    print(
        f"\nFailed to generate a schedule after {max_attempts} attempts. This can happen if constraints are too tight.")
    print("You might need to adjust your double-play pairs or fixed matchups if a solution cannot be found.")
    return None

# --- Generate and Print the Schedule ---
generated_schedule = generate_fantasy_schedule()

if generated_schedule:
    print("\n--- Your Fantasy Football 14-Week Schedule ---")
    for week, matchups in sorted(generated_schedule.items()):
        print(f"Week {week}:")
        for matchup in matchups:
            print(f"  {matchup[0]} vs {matchup[1]}")

    # --- Verification (Optional, but good for checking constraints) ---
    print("\n--- Schedule Verification ---")
    final_matchup_counts = defaultdict(int)
    last_played_verification = defaultdict(int)  # For verifying the minimum weeks between repeat constraint

    for week, matchups in generated_schedule.items():
        teams_in_week = set()
        for team1, team2 in matchups:
            # Check for teams playing themselves or playing twice in one week
            if team1 == team2:
                print(f"ERROR: {team1} playing itself in Week {week}!")
            if team1 in teams_in_week or team2 in teams_in_week:
                print(f"ERROR: Duplicate team in Week {week} matchups: {team1} or {team2}!")
            teams_in_week.add(team1)
            teams_in_week.add(team2)

            pair_fs = frozenset({team1, team2})
            final_matchup_counts[pair_fs] += 1

            # Verify minimum weeks between repeat constraint
            if last_played_verification[pair_fs] > 0 and week - last_played_verification[
                pair_fs] < MIN_WEEKS_BETWEEN_REPEAT:
                print(
                    f"WARNING: {team1} vs {team2} playing in Week {week}, less than {MIN_WEEKS_BETWEEN_REPEAT} weeks after playing in Week {last_played_verification[pair_fs]}!")
            last_played_verification[pair_fs] = week

    # Check if all pairs played the correct number of times
    all_counts_correct = True
    all_possible_pairs_fs = {frozenset({t1, t2}) for t1, t2 in itertools.combinations(teams, 2)}

    for pair_fs in all_possible_pairs_fs:
        expected_count = 2 if pair_fs in {frozenset(p) for p in double_play_pairs} else 1
        actual_count = final_matchup_counts[pair_fs]
        if actual_count != expected_count:
            team_names = tuple(pair_fs)
            print(
                f"WARNING: {team_names[0]} vs {team_names[1]} played {actual_count} time(s), expected {expected_count}!")
            all_counts_correct = False

    if all_counts_correct and all(len(generated_schedule[w]) == len(teams) // 2 for w in range(1, num_weeks + 1)):
        print("All matchup counts and weekly assignments verified successfully!")
    else:
        print("Verification completed with warnings/errors. Please review the schedule and the output above.")
else:
    print("\nSchedule generation failed. Please check the provided constraints and try again.")
