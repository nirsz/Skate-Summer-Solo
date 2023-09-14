import random
import pandas as pd

def roll_dice(num_dice, balance_die_faces):
    """Simulate rolling a variable number of dice each with the same custom faces."""
    results = [random.choice(balance_die_faces) for _ in range(num_dice)]
    print(results)
    print(results.count("Move"))
    return results.count("Move")

# Load the card details from an Excel file
cards = pd.read_excel('TonyCards.xlsx')


# Define the balace and directional dice faces
balance_die_faces = ["Move", "Move", "Move", "Move", "None", "None"]
direction_die_faces = ["+", "+", "+", "-", "-", "-"]


# Define the initial state of Tony Bot
tony_bot = {
    "Street": 1,
    "Vert": 1,
    "Rail": 1,
    "flame_tokens": 2,
    "score": 0,
    "balance": 0  # Balance track position, where 0 is the center, -X is riskier, and +X is safer
}

# Define the trick scores
trick_scores = {
    "Simple": 2,
    "Moderate": 3,
    "Complex": 4,
    "Special": 5
}

# Shuffle the cards before starting the simulation
cards = cards.sample(frac=1).reset_index(drop=True)
# for index, row in cards.iterrows():
#    print(f"index:  {index} ============================================================")
#    print(row)

current_card_index = 0

# Simulate 5 rounds of gameplay
for round_num in range(5):
    print(f"Round {round_num + 1} -------------------------------------------------")

    # Reset balance to 0 at the start of each round
    tony_bot["balance"] = 0

    # Combo phase
    combo_score = 0
    skill_data = []
    
    # j is counting how many cards is drawn in each combo phase
    j = 0
    
    for i, card in cards.iloc[current_card_index:].iterrows():
        if j==0 and card['Trick Type'] == 'Special':
            print(f'Special card was drawn in iteration {j}')
            continue
        
        j+=1
        
        # print(f"Iteration index: {i}")
        print(f"Card Drawn: {card['Card Number']}|| Card Type: {card['Trick Type']}")
        
        # Perform the trick and adjust the balance
        if tony_bot["balance"] < 0:
            tony_bot["balance"] += card["Balance Modifier"]
        else:
            tony_bot["balance"] -= card["Balance Modifier"]
            
        combo_score += trick_scores[card["Trick Type"]] * tony_bot[card["Skill Upgrade"]]
        
        # Check what is the next card's back
        # To refer to the next card, you can use 'i+1' as the index to access the next row
        # But first, you need to check if 'i+1' is a valid index to avoid an IndexError
        next_card = None
        
        if i < len(cards) - 1:
            next_card = cards.iloc[i+1]
        # Now 'next_card' holds the data for the next card, and you can refer to its columns like 'next_card["Column Name"]'
        print(f"Next card: {next_card['Card Number']}")
        
        if next_card is None:
            print(f"No next card")
            break
        
        # gain flame tokens
        tony_bot["flame_tokens"] += next_card["Flame Tokens (Back)"]
        print(f"Flame token gained: {next_card['Flame Tokens (Back)']}")
        
        # Roll balance die
        balace_die_results = roll_dice(j, balance_die_faces)
        direction_die_result = random.choice(direction_die_faces)
        print(f'Balace Die Result: {balace_die_results}')
        print(f'Direction Die Result: {direction_die_result}')

        
        print(f'Balance before balance die: {tony_bot["balance"]}')
        if direction_die_result == "+":
            tony_bot["balance"] += balace_die_results
        else:
            tony_bot["balance"] -= balace_die_results
        print(f'Balance after balance die: {tony_bot["balance"]}')
        
        if card["Skill Upgrade"] not in skill_data:
            skill_data.append(card["Skill Upgrade"])
        print(skill_data)

        # Check if Tony Bot busts
        if tony_bot["balance"] <= -4 or tony_bot["balance"] >= 4:
            tony_bot["flame_tokens"] //=2
            combo_score //=2
            print(f"Tony busted after {i+1} cards total and {j} cards in this round")
            current_card_index = i +1
            break
        
        # Break after maximum of 5 cards played 
        if j==5:
            break
        # Check if Tony Bot lands the combo using next_card
        if next_card["Combo Continuation (Back)"] == "Land":
            if (j == 1 and (card["Trick Type"] in ("Simple", "Moderate"))):
                continue
            else:
                current_card_index = i +1
                print(f"Tony landed after {j} cards in this round")
                break

    # Add the combo score to Tony Bot's total score
    tony_bot["score"] += combo_score
    
    if tony_bot["score"] >= 70:
        print(f'Score of 70 reached, ending game after {round_num+1} rounds')
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

    # Print the state of Tony Bot at the end of the round
    print(f"Tony Bot state at the end of round {round_num + 1}: {tony_bot}")

# Print Tony Bot's final score at the end of the game
print(f"Tony Bot's final score: {tony_bot['score']}")
