from pyrogram import Client, filters
import openai


async def ai(query):
    openai.api_key = "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" #Your openai api key
    response = openai.Completion.create(engine="text-davinci-002", prompt=query, max_tokens=100, n=1, stop=None, temperature=0.9, timeout=5)
    return response.choices[0].text.strip()
     
async def ask_ai(client, m, message):
    try:
        question = message.text.split(" ", 1)[1]
        # Generate response using OpenAI API
        response = await ai(question)
        # Send response back to user
        await m.edit(f"{response}")
    except Exception as e:
        # Handle other errors
        error_message = f"An error occurred: {e}"
        await m.edit(error_message)


@Client.on_message(filters.command('openai'))
async def openai_ask(client, message):
    if len(message.command) == 1:
       return await message.reply_text("Give an input!")
    m = await message.reply_text("👀")
    await ask_ai(client, m, message)
