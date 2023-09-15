import random
import pandas as pd
import statistics
import matplotlib.pyplot as plt

# Roll balance die to determine how many balance adjustments if at all the players will have to make
def roll_dice(num_dice, balance_die_faces):
    """Simulate rolling a variable number of dice each with the same custom faces."""
    results = [random.choice(balance_die_faces) for _ in range(num_dice)]
    print(results)
    # print(results.count("Adjust"))
    return results.count("Adjust")

def plotresults(final_scores, rounds_ended, cards_drawn):
    # Plotting the final scores as a histogram
    plt.figure()
    plt.hist(final_scores, bins=range(min(final_scores), max(final_scores) + 1), alpha=0.7, edgecolor='black')
    plt.title('Distribution of Final Scores')
    plt.xlabel('Final Score')
    plt.ylabel('Frequency')
    plt.grid(axis='y')
    plt.show()

    # Plotting the number of rounds each game lasted as a line plot
    plt.figure()
    plt.plot(rounds_ended, marker='o')
    plt.title('Number of Rounds Each Game Lasted')
    plt.xlabel('Game Number')
    plt.ylabel('Number of Rounds')
    plt.grid(axis='y')
    plt.show()

    # Plotting the number of cards drawn in each round as a line plot
    plt.figure()
    plt.plot(cards_drawn, marker='o')
    plt.title('Number of Cards Drawn in Each Round')
    plt.xlabel('Round Number')
    plt.ylabel('Number of Cards Drawn')
    plt.grid(axis='y')
    plt.show()

# Load the card details from an Excel file
cards = pd.read_excel('TonyCards.xlsx', sheet_name='Sheet7')


# Define the balace and directional dice faces
balance_die_faces = ["Adjust", "Adjust", "Adjust", "Adjust", "None", "None"]
direction_die_faces = ["+", "+", "+", "-", "-", "-"]


# Global simulation settings
num_of_games = 3
num_of_rounds = 7
final_scores = []
rounds_ended = []
cards_drawn = []
discard_pile = []
tony_risk_aversion_modifier = 0.5

for game_num in range(num_of_games):
    print("                                                          ")
    print(f"Game {game_num + 1} ============================================================")


    # Define the initial state of Tony Bot
    tony_bot = {
        "Street": 1,
        "Vert": 1,
        "Rail": 1,
        "flame_tokens": 2,
        "score": 0,
        "balance": 0,  # Balance track position, where 0 is the center, -X is riskier, and +X is safer
        "risk_aversion": tony_risk_aversion_modifier
    }

    # Define the trick scores
    trick_scores = {
        "Simple": 2,
        "Moderate": 3,
        "Complex": 4,
        "Special": 5
    }
    
    discard_pile = []

    # Shuffle the cards before starting the simulation
    cards = cards.sample(frac=1).reset_index(drop=True)
    # for index, row in cards.iterrows():
    #    print(f"index:  {index} ============================================================")
    #    print(row)

    current_card_index = 0

    # Simulate 5 rounds of gameplay
    for round_num in range(num_of_rounds):
        print("                                                          ")
        print(f"Round {round_num + 1} -------------------------------------------------")

        # Reset balance to 0 at the start of each round
        tony_bot["balance"] = 0

        # Combo phase
        combo_score = 0
        skill_data = []
        
        # j is counting how many cards is drawn in each combo phase
        j = 0
        
        # Draw cards in combo phase
        for i, card in cards.iloc[current_card_index:].iterrows():
            
            # Next card in round.
            j+=1
            
            # First card cannot be Special or Complex
            if j==1 and (card['Trick Type'] == 'Special' or card['Trick Type'] == 'Complex'):
                print(f'{card["Trick Type"]} card was drawn in iteration {j}')
                # This card doesn't count so reset card counter to zero and add card to discard pile
                j = 0
                discard_pile.append(card)
                print(f'First card Special or Complex, added to Discard pile. Currnet discard pile size is {len(discard_pile)}')
                continue
            elif j==2 and card['Trick Type'] == 'Special':
                print(f'{card["Trick Type"]} card was drawn in iteration {j}')
                # This card doesn't count so reset card counter to 1 and add card to discard pile
                j = 1
                discard_pile.append(card)
                print(f'First card Special or Complex, added to Discard pile. Currnet discard pile size is {len(discard_pile)}')
                continue

            
            
            print(f"Total card index in deck: {i}")
            print(f"Number card in this round: {j}")

            print(f"Card Number Drawn: {card['Card Number']}|| Card Type: {card['Trick Type']}")
            
            # Perform the trick and adjust the balance
            if tony_bot["balance"] == 0:
                # Randomly choose between "+" and "-"
                operator = random.choice(["+", "-"])
                if operator == "+":
                    tony_bot["balance"] += card["Balance Modifier"]
                else:
                    tony_bot["balance"] -= card["Balance Modifier"]
            elif tony_bot["balance"] < 0:
                tony_bot["balance"] += card["Balance Modifier"]
            else:
                tony_bot["balance"] -= card["Balance Modifier"]
                
            combo_score += trick_scores[card["Trick Type"]] * tony_bot[card["Skill Upgrade"]]
            
            # Check what is the next card's back
            next_card = None
            if i < len(cards) - 1:
                next_card = cards.iloc[i+1]
            print(f"The next card is: {next_card['Card Number']}")
            
            if next_card is None:
                print(f"No next card")
                cards_drawn.append(j)
                break
            
            # Gain flame tokens from the back of the next card
            tony_bot["flame_tokens"] += next_card["Flame Tokens (Back)"]
            print(f"Flame tokens gained: {next_card['Flame Tokens (Back)']}")
            
            # Roll balance die
            balace_die_results = roll_dice(j, balance_die_faces)
            direction_die_result = random.choice(direction_die_faces)
            print(f'Balace Die Result: {balace_die_results}')
            print(f'Direction Die Result: {direction_die_result}')

            # Adjust balance based on dice results
            print(f'Balance before balance die: {tony_bot["balance"]}')
            if direction_die_result == "+":
                tony_bot["balance"] += balace_die_results
            else:
                tony_bot["balance"] -= balace_die_results
            print(f'Balance after balance die: {tony_bot["balance"]}')
            
            # Add the skills we will need to upgrade at the end of the round
            if card["Skill Upgrade"] not in skill_data:
                skill_data.append(card["Skill Upgrade"])
            print(f'Current skills to upgrade after {j} cards: ', skill_data)

            # Check if Tony Bot busts
            if tony_bot["balance"] <= -4 or tony_bot["balance"] >= 4:
            
                #Half their combo score and flame tokens rounded down
                tony_bot["flame_tokens"] //=2
                combo_score //=2
                print(f"Tony busted after {i+1} cards total, including skipped, and {j} cards in this round")
                
                # put last card in the discard pile
                discard_pile.append(card)
                print(f'Currnet discard pile size is {len(discard_pile)}')
                
                current_card_index = i + 1
                cards_drawn.append(j)
                break
            
            # Break after maximum of 6 cards played 
            if j==6:
                
                # put last card in the discard pile
                discard_pile.append(card)
                print(f'Currnet discard pile size is {len(discard_pile)}')
                
                cards_drawn.append(j)
                break
            
            # Check if Tony Bot lands the combo using next_card
            if next_card["Combo Continuation (Back)"] == "Land":
                if (j == 1 and (card["Trick Type"] in ("Simple", "Moderate"))):
                    continue
                elif random.random() <= tony_bot["risk_aversion"]:
                    current_card_index = i + 1
                    print(f"Tony chose to land due to high risk aversion after {j} cards in this round")
                    
                    discard_pile.append(card)
                    print(f'Currnet discard pile size is {len(discard_pile)}')
                    
                    cards_drawn.append(j)
                    break

        # Add the combo score to Tony Bot's total score
        tony_bot["score"] += combo_score
        
        if tony_bot["score"] >= 70:
            print(f'Score of 70 reached, ending game after {round_num+1} rounds')
            rounds_ended.append(round_num+1)
            print(f"Tony Bot state at the end of round {round_num + 1}: {tony_bot}")

            break

                
        # Upgrade and scoring phase
        # Upgrade the cheapest skills in the skill collection for the card for this round
        while tony_bot["flame_tokens"] > 0:
            # Find the skill with the lowest upgrade cost
            cheapest_skill = min(skill_data, key=lambda skill: tony_bot[skill] + 1)
            upgrade_cost = tony_bot[cheapest_skill] + 1

            # Check if there are enough flame tokens to upgrade the cheapest skill
            if tony_bot["flame_tokens"] >= upgrade_cost:
                # Upgrade the skill
                tony_bot[cheapest_skill] += 1
                # Deduct the upgrade cost from the flame tokens
                tony_bot["flame_tokens"] -= upgrade_cost
            else:
                # If not enough flame tokens to upgrade the cheapest skill, break out of the loop
                break

        # If it's the last round just add it to the rounds ended list
        if round_num+1 == num_of_rounds:
            rounds_ended.append(num_of_rounds)
        # Print the state of Tony Bot at the end of the round
        print(f"Tony Bot state at the end of round {round_num + 1}: {tony_bot}")

    # Print Tony Bot's final score at the end of the game
    print(f"Tony Bot's final score: {tony_bot['score']}")
    
    final_scores.append(tony_bot['score'])
    
# Print the summary of all scores at the end of the 10 games
print(f"Final scores of all {num_of_games} games: ", final_scores)
print(f"Games ended in the following rounds: ", rounds_ended)
print(f"Number of cards drawn in each round: ", cards_drawn)
print("Average score: ", round(sum(final_scores) / num_of_games))
print("Standard deviation: ", round(statistics.stdev(final_scores)))  # Round the standard deviation to the nearest whole number

score_range = max(final_scores) - min(final_scores)
print("Difference between highest and lowest score: ", score_range)

# plotresults(final_scores, rounds_ended, cards_drawn)





