from telegram import Update
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackContext

# Define conversation states for better management of user inputs
ADDING_HABIT, FREQUENCY, TRACKING = range(3)

# Dictionary to store user habits in-memory (for demonstration purposes)
user_habits = {}

def start(update: Update, context: CallbackContext):
    # Send a welcome message and instructions
    update.message.reply_text('Hello! I am your healthy habit tracker bot.\n'
                              'Use /addhabit to add a new healthy habit.')
    return ConversationHandler.END

def add_habit(update: Update, context: CallbackContext):
    # Prompt the user to enter a new healthy habit
    update.message.reply_text('Please enter the healthy habit you would like to add (e.g., "Drink 3 glasses of water daily").')
    return ADDING_HABIT

def frequency(update: Update, context: CallbackContext):
    # Ask for the frequency of the habit after receiving the habit input
    habit = update.message.text
    context.user_data['habit'] = habit
    update.message.reply_text('How often do you want to do this habit? (e.g., "daily", "3 times a week")')
    return FREQUENCY

def save_habit(update: Update, context: CallbackContext):
    # Save the habit and its frequency to the in-memory storage
    frequency = update.message.text
    habit = context.user_data['habit']
    user_id = update.message.from_user.id
    if user_id not in user_habits:
        user_habits[user_id] = []
    user_habits[user_id].append({'habit': habit, 'frequency': frequency, 'count': 0})
    update.message.reply_text(f'Habit "{habit}" with frequency "{frequency}" added!')
    return ConversationHandler.END

def track_habit(update: Update, context: CallbackContext):
    # Display the user's habits and ask which one was completed
    user_id = update.message.from_user.id
    if user_id not in user_habits or not user_habits[user_id]:
        update.message.reply_text('No habits added yet! Use /addhabit to add some.')
        return ConversationHandler.END
    habits_info = '\n'.join([f"{idx + 1}. {habit['habit']} ({habit['frequency']}) - Tracked {habit['count']} times"
                             for idx, habit in enumerate(user_habits[user_id])])
    update.message.reply_text(f'Your habits:\n{habits_info}\n\n'
                              'Reply with the number of the habit you just completed.')
    return TRACKING

def update_tracking(update: Update, context: CallbackContext):
    # Update the tracking counter for a habit based on user input
    habit_number = int(update.message.text) - 1
    user_id = update.message.from_user.id
    if habit_number < 0 or habit_number >= len(user_habits[user_id]):
        update.message.reply_text('Invalid habit number. Please try again.')
        return TRACKING
    user_habits[user_id][habit_number]['count'] += 1
    habit = user_habits[user_id][habit_number]
    update.message.reply_text(f'Well done! You have completed "{habit["habit"]}" now {habit["count"]} times.')
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    # Allow the user to cancel the current operation
    update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

def main():
    token = 'YOUR_TOKEN'
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # Define a conversation handler to manage different states of the conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CommandHandler('addhabit', add_habit),
                      CommandHandler('track', track_habit)],
        states={
            ADDING_HABIT: [MessageHandler(Filters.text & ~Filters.command, frequency)],
            FREQUENCY: [MessageHandler(Filters.text & ~Filters.command, save_habit)],
            TRACKING: [MessageHandler(Filters.text & ~Filters.command, update_tracking)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()