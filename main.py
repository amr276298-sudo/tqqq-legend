import os, threading, yfinance as yf, ta
import telebot
from flask import Flask
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "GOD BOT LIVE"
def god():
    try:
        t=yf.Ticker("TQQQ"); h=t.history(period="3mo")
        c=h['Close']; last=c.iloc[-1]; prev=c.iloc[-2]; pct=(last-prev)/prev*100
        rsi=ta.momentum.RSIIndicator(c,14).rsi().iloc[-1]
        sma50=ta.trend.SMAIndicator(c,50).sma_indicator().iloc[-1]
        sma200=ta.trend.SMAIndicator(c,200).sma_indicator().iloc[-1]
        atr=ta.volatility.AverageTrueRange(h['High'],h['Low'],c,14).average_true_range().iloc[-1]
        rec=h.tail(20); buy=rec[rec['Close']>rec['Open']]['Volume'].sum(); sell=rec[rec['Close']<rec['Open']]['Volume'].sum()
        buy_pct=buy/(buy+sell)*100 if buy+sell>0 else 50
        sh=h['High'].tail(20).max(); sl=h['Low'].tail(20).min()
        try:
            exp=t.options[0]; chain=t.option_chain(exp)
            bc=chain.calls.iloc[(chain.calls['strike']-last).abs().argsort()[:3]].sort_values('openInterest',ascending=False).iloc[0]
            bp=chain.puts.iloc[(chain.puts['strike']-last).abs().argsort()[:3]].sort_values('openInterest',ascending=False).iloc[0]
            ci=f"${bc['strike']} (${bc['lastPrice']:.2f})"; pi=f"${bp['strike']} (${bp['lastPrice']:.2f})"
        except: ci=f"${last*1.02:.0f}"; pi=f"${last*0.98:.0f}"
        score=0
        if last>sma50: score+=2
        if last>sma200: score+=2
        if 40<rsi<70: score+=1
        if buy_pct>55: score+=2
        if rsi>75: score-=2
        call=max(5,min(95,int((score+6)/12*100))); put=100-call
        dec="CALL 🚀 "+ci if call>=70 else "PUT 🔻 "+pi if put>=70 else "انتظار ⚖️"
        stop=last-atr*1.5 if call>50 else last+atr*1.5; tgt=last+atr*3 if call>50 else last-atr*3
        return f"🔱 GOD BOT\n💵 ${last:.2f} ({pct:+.2f}%) RSI {rsi:.1f}\nشراء {buy_pct:.0f}% | بيع {100-buy_pct:.0f}%\nدعم ${sl:.2f} مقاومة ${sh:.2f}\nCALL {ci} | PUT {pi}\nوقف ${stop:.2f} هدف ${tgt:.2f}\n🎯 {dec}\nCALL {call}% PUT {put}%"
    except Exception as e: return f"جاري التحميل... {e}"
@bot.message_handler(commands=['start'])
def s(m): bot.reply_to(m, god())
@bot.message_handler(func=lambda m: True)
def a(m): bot.reply_to(m, god())
def run(): bot.infinity_polling()
threading.Thread(target=run).start()
if __name__=="__main__": app.run(host='0.0.0.0',port=10000)
