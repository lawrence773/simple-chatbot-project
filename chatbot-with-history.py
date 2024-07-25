from openai import OpenAI

client = OpenAI()

# If you don't have an API key in the system environment:
# client = OpenAI(api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


class ChatHistory:
  def __init__(self, system_message, number):
    # self.system_message = system_message
    self.history = [{"role": "system", "content": system_message}]
    self.number = number

  def add_message(self, message_role, message_content):
    self.history.append({"role": message_role, "content": message_content})

    # Because of OpenAI token usage, I will limit the number of texts stored
    if len(self.history) > self.number:
      self.history.pop(1)

  def add_user_message(self, message_content):
    self.add_message("user", message_content)

  def add_bot_message(self, message_content):
    self.add_message("assistant", message_content)

  def retrieve_messages(self):
    return self.history

  def summarise_history(self):
    # Converting history to a single text
    full_text = ' '.join([msg["content"] for msg in self.history if msg["role"] != "system"])

    # Summarising the past conversation using the chat completions endpoint
    response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "Summarise the most important facts and decisions of the past conversation."},
        {"role": "user", "content": full_text}
      ]
    )

    summary = response.choices[0].message.content.strip()
    return summary

message_history = ChatHistory("You are witty, somewhat offensive but funny, you sound like Ricky Gervais. "
                                    "Try to respond in one concise sentence."
                                    "If summary is expected of you, then precision is your top priority, not being funny."
                                    "Take your time to think about the request before answering.", number = 7)

def chat_with_bot(prompt):
  message_history.add_user_message(message_content=prompt)

  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=message_history.retrieve_messages()
  )

  bot_message_content = response.choices[0].message.content.strip()
  message_history.add_bot_message(bot_message_content)
  return bot_message_content

# if __name__ == "__main__":
while True:
  user_input = input("You: ")
  if user_input.lower() in ["quit", "exit", "stop", "bye"]:
    break
  elif user_input.lower() in ["summarise", "summarize", "summary", "sum up"]:
    final_summary = message_history.summarise_history()
    print(f"'Summary of past conversation: ', {final_summary}")
    continue

  response = chat_with_bot(user_input)
  print(f"'Chatbot: ', {response}")