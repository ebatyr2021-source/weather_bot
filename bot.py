import io
import logging
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔑 Токены
TOKEN = "8265923232:AAEukdI-Xm3r7tPOZke3EZ1bT-pGbF-0Jbs"
API_KEY = "88f8b680942555d9d07778f85df0f485"

# Логирование
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger("weather-bot")

# Получение данных погоды с OpenWeatherMap
def fetch_weather(city="Temirtau", api_key=API_KEY):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=ru"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data

# Построение графика температуры
def plot_weather(data):
    times = [item["dt_txt"] for item in data["list"][:16]]  # первые ~2 дня (шаг 3 часа)
    temps = [item["main"]["temp"] for item in data["list"][:16]]

    fig, ax = plt.subplots(figsize=(10,5), dpi=120)
    ax.plot(times, temps, marker="o")
    ax.set_xlabel("Время")
    ax.set_ylabel("Температура, °C")
    ax.set_title("Прогноз погоды для Темиртау (OpenWeatherMap)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

# Команда /forecast
async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = fetch_weather("Temirtau")
    except Exception as e:
        logger.exception(e)
        return await update.message.reply_text("Ошибка при получении данных погоды.")

    img = plot_weather(data)

    # Формируем текстовый прогноз на ближайшие часы
    forecast_text = "Прогноз погоды для Темиртау:\n\n"
    for item in data["list"][:5]:  # первые 5 значений (15 часов)
        dt = item["dt_txt"]
        temp = item["main"]["temp"]
        desc = item["weather"][0]["description"]
        forecast_text += f"{dt}: {temp:.1f}°C, {desc}\n"

    await update.message.reply_photo(photo=img, caption=forecast_text)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот-прогнозист для Темиртау 🌤\n"
        "Напиши команду /forecast, чтобы получить прогноз погоды."
    )

# Основная функция
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("forecast", forecast))
    app.run_polling()

if __name__ == "__main__":
    main()