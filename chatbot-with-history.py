from openai import OpenAI

client = OpenAI()

# If you don't have an API key in the system environment, use the below line to add your own OpenAI API key:
# client = OpenAI(api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

#Creating a class to manage conversation history and interactions with the OpenAI model:
class ChatHistory:
  def __init__(self, system_message, number):
    #Storing conversations as lists of dictionaries:
    self.history = [{"role": "system", "content": system_message}]
    
    #To limit the number of messages in the conversation:
    self.number = number

  #Adding a message to the chat history:
  def add_message(self, message_role, message_content):
    self.history.append({"role": message_role, "content": message_content})

    # Because of OpenAI token usage, I will limit the number of texts stored. See below at message_history.
    if len(self.history) > self.number:
      self.history.pop(1)

  #Separating messages into user and bot:
  def add_user_message(self, message_content):
    self.add_message("user", message_content)

  def add_bot_message(self, message_content):
    self.add_message("assistant", message_content)

  #To retrieve conversation history:
  def retrieve_messages(self):
    return self.history

  #To summarise the conversation history using the OpenAI API:
  def summarise_history(self):
    # Converting history to a single text
    full_text = ' '.join([msg["content"] for msg in self.history if msg["role"] != "system"])

    # Summarising the past conversation using the chat completions endpoint. I've used gpt-4o mini as it's cheaper and more efficient than 3.5-turbo:
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "Summarise the most important facts and decisions of the past conversation."},
        {"role": "user", "content": full_text}
      ]
    )

    summary = response.choices[0].message.content.strip()
    return summary

#Creating an instance of the ChatHistory class. The bot will remember 7 past messages to keep the API requests cheap:
message_history = ChatHistory(
  "You are witty, somewhat offensive but funny, you sound like Ricky Gervais. A hint of morbidity is allowed."
  "You are an expert in history. You make funny comparisons between historical accounts and present-day pop cultural events."
  "Try to respond in one concise sentence."
  "Take your time to think about the request before answering.", number = 7)

#The below function handles the conversation between the user and the bot using OpenAI API. It takes the users input (prompt) and sends it to OpenAI API for analysis. 
#The bot message is sent back and the conversation is stored.  
def chat_with_bot(prompt):
  message_history.add_user_message(message_content=prompt)

  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=message_history.retrieve_messages()
  )

  bot_message_content = response.choices[0].message.content.strip()
  message_history.add_bot_message(bot_message_content)
  return bot_message_content

# Creating an infinite loop that keeps the bot running until the user specifically interrupts it:
while True:
  user_input = input("You: ")
  if user_input.lower() in ["quit", "exit", "stop", "bye"]:
    break
  elif user_input.lower() in ["summarise", "summarize", "summary", "sum up"]:
    final_summary = message_history.summarise_history()
    print(f"Summary of past conversation: {final_summary}")
    continue

  response = chat_with_bot(user_input)
  print(f"Chatbot: {response}")
