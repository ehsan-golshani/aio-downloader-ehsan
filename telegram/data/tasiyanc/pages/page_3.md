# آرشیو کانال tasiyanc - صفحه 3

📅 آخرین بروزرسانی: 1405/03/01 02:51

---

## tasiyanc — post 5221

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
Tarkibi 🔐 📱


{
"dns": {
"hosts": {
"domain:googleapis.cn": "googleapis.com"
},
"servers": [
"1.1.1.1"
]
},
"inbounds": [
{
"listen": "127.0.0.1",
"port": 10808,
"protocol": "socks",
"settings": {
"auth": "noauth",
"udp": true,
"userLevel": 8
},
"sniffing": {
"destOverride": [
"http",
"tls"
],
"enabled": true,
"routeOnly": false
},
"tag": "socks"
},
{
"listen": "127.0.0.1",
"port": 10809,
"protocol": "http",
"settings": {
"auth": "noauth",
"udp": true,
"allowTransparent": false
},
"sniffing": {
"destOverride": [
"http",
"tls"
],
"enabled": true,
"routeOnly": false
},
"tag": "http"
},
{
"listen": "127.0.0.1",
"port": 1053,
"protocol": "dokodemo-door",
"settings": {
"address": "1.1.1.1",
"network": "tcp,udp",
"port": 53
},
"tag": "dns-in"
}
],
"outbounds": [
{
"tag": "proxy",
"protocol": "vless",
"settings": {
"vnext": [
{
"address": "bab-6.site",
"port": 443,
"users": [
{
"id": "b585dc5e-55bf-4a8b-913a-27c9ccac05c3",
"alterId": 0,
"email": "t@t.tt",
"security": "auto",
"encryption": "none",
"flow": ""
}
]
}
]
},
"streamSettings": {
"network": "ws",
"security": "tls",
"tlsSettings": {
"allowInsecure": false,
"alpn": [
"http/1.1"
],
"fingerprint": "chrome",
"serverName": "bab-6.site",
"show": false
},
"wsSettings": {
"headers": {
"Host": "bab-6.site"
},
"path": "/vws/"
},
"sockopt": {
"tcpNoDelay": true,
"tcpKeepAliveIdle": 60
}
}
},
{
"tag": "fragment",
"protocol": "freedom",
"settings": {
"domainStrategy": "AsIs",
"fragment": {
"packets": "1-3",
"length": "8-12",
"interval": "2-4"
}
},
"streamSettings": {
"sockopt": {
"tcpNoDelay": true,
"tcpKeepAliveIdle": 60
}
}
},
{
"protocol": "freedom",
"settings": {
"domainStrategy": "UseIP"
},
"tag": "direct"
},
{
"protocol": "blackhole",
"settings": {
"response": {
"type": "http"
}
},
"tag": "block"
}
],
"policy": {
"levels": {
"8": {
"connIdle": 300,
"downlinkOnly": 1,
"handshake": 4,
"uplinkOnly": 1
}
},
"system": {
"statsOutboundUplink": true,
"statsOutboundDownlink": true
}
},
"remarks": "Tasiyanc tkb",
"routing": {
"domainStrategy": "IPIfNonMatch",
"rules": [
{
"ip": [
"1.1.1.1"
],
"outboundTag": "proxy",
"port": "53",
"type": "field"
}
]
},
"entryDomain": "bab-6.site:443"
}

تست کنین ترکیبی بهم بگید
Join As 🩵@Tasiyanc 
☑️
</div>

## tasiyanc — post 5220

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
📶 اختصاصی تاسیان   📶

برای اتصال پایدار زمان مناسب بدید😐

Join As 🩵@Tasiyanc 
☑️
</div>

## tasiyanc — post 5219

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
🥇 DNSTT Tcp 🇩🇪

slipnet-enc://AcNagZVmSOeXnC5m8fl/SxZp1519lU/0c05yrGx71EVPzJ5DBuJpWMc002i+Qqxocfm2IbyxubP+rzzD3d1pElmwLEyHXcZ+xb68XE/1SCQmQ61TFWv+hbfwFbVXHqvikWFjvWw+/N2ai4prlQHLlJ275QNtzDph/AFGAgudFgtB21JIn0XWhXRnFg2z8w5J0o6GDGRr1Ngus8cz+41EbYGXpk7GU4zyOJijzZjXdiWRH9Z3SHuvsS2jnOg/ObhJ+Ngapw34BqhwxME2/c+b+eewEDEh/4VD8cOmnpqWSpB8rPs+IB9MvxFN+hcTdhE3hEA55nijuARMm06Pukk2e/2Z0aQmBKa4Gl14mqosRJE8nCFVYAL6ZHQpyh7chhRol5bKm/bK6qxnL43LSur6VirpaZYo2+KmYfRJE6YnYzph664QwKC5A3IDBHHVPctQvAfcOe00b0MYb5SWklJkZMosa7+jZ/VEwfu1mI0vpQ92Am5HIm5U2bGpE+JrL9bO5plbkpeXYzTSAtrymXXkZ1e8oxW/uf7qztAYvTNkaGJDBZpxBc0rTnw0p9GhLnah+kaK7rxxZYJ0cRayDUADW0WXLb6TSJ6olvBM1rOAoy2jRuBkT0ndpsXliVCRIn7O55sR801uPxrjIMFHnYWZs/UqWaEiORxsXEuC03dt2TlUy7IBYmSyiQ0Btn5AcyM2rm+okZ5KcKrDCXkh558q+igXvtcjGFpgULI5utVhxUVTr4FUF59SlZpULBWBdONk1TSOjWDpIQu0+5KMdhfelPzaNVE=

Join as @Tasiyanc 
☑️
</div>

## tasiyanc — post 5218

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
📶 اختصاصی تاسیان   📶

برای اتصال پایدار زمان مناسب بدید😐

Join As 🩵@Tasiyanc 
☑️
</div>

## tasiyanc — post 5217

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
صبحتون بخیرررر
</div>

## tasiyanc — post 5216

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
😎VyDns 🇩🇰

slipnet-enc://AWxKUtwcMohoM20dWSihPh/zDfSR6mpUYrSUkfDsDR172SODbMbh3ELmq9sQTRLbAsX5Z8Cvryvb8QzQgZtfqSuNeDcpTiW76Uky+OmvLADNJAFBNeGh2m2vcbXpy6ojPDAW8hLbgADLqG2PHpS8qvMwRffpUWiK7dV58ZPGZCeMf7ULklZhF+PLnKymYyCoY9Ibsq/9EF80t+DW8XSu+FWCot72SJ6KcYeWm7Bhq+f1LU2blpfTyAPKYiMXwToaSgEv0hseYbtRQCe9goLoiBfcayYqowHgrfk4VKtIUAYofFMnogOTOYNU4D1LezT0Q93F4oFlnqUrVWEkK3/ypYkA4Q7h6d0rmsl3oN8bcaz/Y1uaAypmzAl6I7wsQBWxAp4lQL1s8RjU+xYw03mj5u6zwp+QwcltINGCVz55WB6uoJabeQl1uKs/kqPP9efBeQmXFcb34kO4YEanCO1bLwTEhfJxfpyzZJDcz1uIqOAGm/5kNM6B/Gw53jezm/Nq5NiB0gcWQrqxeeSruP9i1zgI6wuewzKrJyYZxnnRxgEpz/+aEEcOA5nARDFgznGNeOuhTRIgWol/5lJSuhFGpoW+O2PGWZGIAN0QCwKZtD1agmoa3enJ1drBY380jgmH+3VY1nXpVkmligFkv/glP38hH/Vddttv1J6Xnw3WDO47tgHWeBN+gCPa3lkGskVvXB16piCir5w/DOoDcvZtbqq7vDNLT1ln3rtOeNsTjAWyj8KhXoM2MRWBnnTlAOScEHN3wAOOv/ZmqZL3tg==

Join as @Tasiyanc ☑️
</div>

## tasiyanc — post 5215

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
📶 اختصاصی تاسیان وای‌فای  📶

برای اتصال پایدار زمان مناسب بدید😐

@Tasiyanc 🩵
</div>

## tasiyanc — post 5214

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
🌟SSH - New method 🤩

slipnet-enc://ATf7my1QlphNrQKA889SRsGki4AZvSLx4SDmE515JrRJP0/EgyXdR+YxlPrdDrfEZ4j2dwMLGq+/lK2F6LCDA5jjJjzPnxl5nzW2n8RVU9qq4aSzE92Zeumrsv06uydZD5lMrDt50lu5YpPDtrlw0RGW3499XZBI1gol0Tzhk5uKQ2ORy4Wt1s7+y/LlCrWy/hgVgF09GaFzTg47WHxd0Cs+B3tv5m4qOHMhnAx/UH4amgqB7D8bDm8d+DiHA8WLP7uLbVEbPREMWSw3PTCwFYgn1ZMOJYXhzWDzXBzzCMp9qyUoLVvZT0V6scm//TRWnqtgO6IE98wGwH8MN6ROsr7awGgmX/iEvIJp4mH0cDapt+gb/BZKysJBhFSAp5wwV9SCpDRfr4wL49dBIJyGPuvijJUdT7hhCRwsrdejICQEW4HJJS+ZTUB1b4pNdF3yFayMoqKMrCzyISW+onPYCbAOz89Gn4D/1O1rEPU6P71Rh+KkmYVAo/vjU+s6eg==

Join as @Tasiyanc ☑️
</div>

## tasiyanc — post 5213

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
🛡 🌟

slipnet-enc://AVE7PohoSt6uWpl0QeAEtPG5bxVDAPlYcE1llXvA07obK3p9Dsq+eOXsO71j+KVLSOYSQCUIGT8vZBUzsX18MW6Hki6ORP0j/H5AsYI8wDg7PXD+7Gn53MvECyaq8P60WglUC/lhiI44/pV8EdaX4ueaC5JqTchJD9k3orRk7Goagc6GbpT/ji+UVq3TohdsLITtDTshOBpgDlXdwTLvpYBiqlPRKFbL8ley3ebEZBV7yM//XzHZZjOPpRwAtWVYWGRGK2kjqiXwHGwQbSzGOdBNn8jOF//65YDYRPfhKjBY2DAXmHrTCRxTjrnYgaZfXVLT6ZWHF8JiOYHzm3JEckLUur/I4TjC56l2W2sYU9M3rETHXy3RmoljEaoBntZ9Ye0cuqMr+sTI0VP68d0iVtWiohHZbKut6FEygSiSR7YTuQPHBA9Tf2QkmpcoDtTiwJlZVM/aPnZc5UGK8npKC7qxSn/aqkjBOuiku6AC3bnntbed/FX0KTJPsjuRutskErUF+XH7Cdn6mtZGb3hR/GAOa2IIYN0uEv12eOthBcXwisA30/sLFNG4CLcfEDazZ9zFpAoyb8gstxhr1LoMGrXvGDX+94E9ZWSgAmTmg7+1Kc802pBXSv/MPUTuNKcS+JTK5KUAFWIcj0fTgHBec+OYXmJ88ikVRG6JX5ZEWCtO2ZBkWxN7aJbxw3yoxiNI6WTybsh7y2B7v4U2eYImSSuNIoOdnOwzNqfF9zGut3PZRhMvHekz6M0m8PzrO4ZR2wcgz+5FspM1

slipnet-enc://Ae1bdKnKMaAVkhaVFC0tbxojRNyFsnzAJMmpy2J6CMVK9pr2XDYzhVKFtggjvaqZptGN8hBUKLoRaToIiq9j/7NfMygv6iyp4vlge+HVX4OJiQNOhLjr+8srmXWvPl+LFpxxETJxsrC+PAy88KyAK1lSMK+3Yih4zwYyJc5NKK5+fROZC0BlCTcF8Qc2NghIi9clKifxepEF9/4JPoH5m/CAXmaR8jv+5qPE3bUOZGXbDpeE4lIXKNNRRc6NP828x1WV488NnDy9YIoaA5u3jzLg0TMpEVOP8cDx6sF5NWd6KRQOc8TTxSZbV6f+Muj8R/gWUxilJ+0uPQCYXqUPE863iaA8hMDVtSKMe8lpx634HLEzAexonsY+ILhzj2rlcPDoPzC7neH28xZMCZsJl82ensR02/LSp2DUeVMlwtWPF3Bn1vH8600GBj3QFK2NvtieZ9w+nLmpm24IP7aCca8a0rYecupB0ZZr0jhUOxpUbcxC6FOIUcB9PiRPVv6K5Ie5AGi6ZUDsq3dc0en0s/mFVqz7HtkelrBDT2jf/zLrXNgVQVEZBNev0lVYLlEerXAzXKkprSYzIc09MB0m3Ie4ZM8bdwr2BQ+jWuhPUanyUM9JVFlFsFha3udIz95MnaHTyP1F3C0yUoZJrJiim+BTXOgM7w62j7oTumXSmgTRiCFhOefgeDpgagFlEbMyhjgxjwAbGphX14bPzr6zjq9X+TE4UEUopO072L4iSAKyS6dW9EdQPOzcxrsaO8W98YtwUu+3

آموزش سایفون

🤩ترکیبی بزنید با سایفون اگه وصل نشد مود پراکسی یا vpn تست کنین

@Tasiyanc
</div>

## tasiyanc — post 5212

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
📶 اختصاصی تاسیان وای‌فای 📶

برای اتصال پایدار زمان مناسب بدید😐

@Tasiyanc 🩵
</div>

## tasiyanc — post 5211

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
DNSTT 🇧🇪

slipnet-enc://AeMf7mMr1HJGkag2PSChX/pjKeXDxb16uNfYxvob0gHrIthcqDq9Q+KhESEAmFqoBA7oIn2W/MOscZFxmb5GSwSs80G2A7hZRrIrlrHdrO0BRu7OnWvmtCUZ8BEYvjJoWab+ZllFgbkWKyE12qHq5fIzbnoXSCAtYAenTPV1DRjMvDFjJOdZ1Vi6VU67aLU65WVaCLXnoEKhMVNJC7tqfxZrReH68dj+G8yFLG0dV6HWxneSULjH/cWbpX22y5RzIPqEFa6XI16rADLLqYerGUJt+Rv6LHhq+sJf3LSwwvjaIcfy/9Us+kUp3QaY/4pGdeDZto6HxUt6eXR/AqE1Q/IkaMEkyeVP+fv6BLXcEGB11XGmWtZsHtxMv5llboIkwqAsgBgV83tVTCjJ5AbVUAVWG0IkTC5CZGljA47gJpW021A0pJ53sLAed34EJPdf3Oxuq2+OHfubOdkD4sho/lDOzJKnDKf7jPW1dSVdb/9IjlIdpdZR97KE1YZuNZ9NyiX8NfZybSKy55D1Tc5T56FkaHamqK+gZlCyduL9UrBsQv3NLlnzLx8j2e4hWSx0p8vlMxwuwTOuBneVSsGs7dsuxUixJyvzWFuMRSVh8rL59Vw9wT/qURSKbAka/7TyTayQ3B8RVbuzKBfQVD7UR5fQ7LiAbwq8SR7PaErA1PRdtS0CXfrn7Kee/C6UP9UClTyBU4Iy+LNRHDOpbLqBRhpbsfmXEp0iqJV2Ta37d8oEnYqnCYYA2olsaNr2ht+ly2PvPa50fZhwP9X5rEGunaoL

@Tasiyanc ☑️
</div>

## tasiyanc — post 5210

## tasiyanc — post 5209

<div align="center"><img src="files/post_5209_tasiyanc_5209.jpg" alt="Photo"></div>

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
@Tasiyanc ✍🏻.npvt
</div>

## tasiyanc — post 5208

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
با وجود اختلالات شدید همچنان در تلاشیم وصل نگه داریم عزیزانو ، کانفیگ ها تست شده ان چون اختلال زیاده کمی زمان بره بیاد بالا پروکسی گذاشتم براش ، امیدوارم وصل بمونید ❤️
</div>

## tasiyanc — post 5207

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
🔐 اختصاصی تاسیان تست شده 🔐

حتما برای اتصال پایدار دو الی پنج دقیقه زمان  بدید و از [ پروکسی ]   کمکی استفاده کنید🚀

Join as @Tasiyanc ☑️
</div>

## tasiyanc — post 5206

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
😎 VyDns SSH 🇷🇺

slipnet-enc://Aaww8PvxLPFu0vkE/TIjc9hYWkVu7OWWdAqZv8BojMszVKFG748E1qv3vVdom8HPa589CsF2TckXpJuxMfZHtxnkJtVzlxR8FEDWSioSqQKLdnMNg8O3+PYW3IC+BjTEAC+SIkVvO7WaIKbFmyVlSkQ576KjLtvJ5sSJIVxbvJz9tWWsUwrmVozg+4O8XpdXFYw9l5iu9IzRs901XONAkpZwDUTun5PG1sXDkINFt4bcglFq7+6EywRK8PuuGftRXd44mxb2sAnk+QRzZS81jN2KS2Go7nfb7N5Ge3g4Wmj2SC9xJlqfKEbwsGVqISPxYSx5zRhRQfl/+sVQ3UytJyFHkRy2HKwuNmdQeHCx7WilpVssGk+bvkbhH3Get3gXEtfT0Z+5YRzl5dISEI3DLTMqgzhPBaWHkoQgZrQOu5NdelJLE33BmM805XTdOIPlcYA0kfpBaOL+kdnd0lG99zt5bXVcuelgmJPxkBhAXA5S8kWlDN+603DsCtwNYgto8Z+3VG2+I9suL4ICkubGf3nC1DP/q3q28/GU2088Z0IR5Zzv0SrHDMGhMezI5+oHwKbgtvRLHXL0OG5BUKD/PmJJFeUMi2lVzXuYjMhVmBkkEiuzFH3jP1erzRTMozQa3wiaPCZBlVQsBqpfo6gs/ujhJT9WPoz5HYHHjSi1qb7qdjAcP7IahMMln55ZCSJE15Yj3qeJSNmtLRZdw5cIrcO5E0UTdCn43W2+UQo6lldt6FzGDqfC4tvAtXxK4fF0ju5GfhLdxtVdIL6nErqMIzF0a8b2IctWdrz/+QuM7xmZFS4b4K9m4sffPqpzskmIa/csfWwFzOLy67uyDjFtQNXvUiZjw4K2//Tdog==

Join as @Tasiyanc ☑️
</div>

## tasiyanc — post 5205

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
📶 اختصاصی تاسیان تست شده 🛜🛜 

حتما برای اتصال پایدار دو الی پنج دقیقه زمان  بدید و از [ پروکسی ] کمکی استفاده کنید🚀

Join as @Tasiyanc ☑️
</div>

## tasiyanc — post 5204

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
📶 اختصاصی تاسیان تست شده 🛜🛜 

حتما برای اتصال پایدار دو الی پنج دقیقه زمان  بدید در صورت ناپایداری پروکسی بزنید 🚀 صبر ندارید نزنید 
✅


@Tasiyanc 🩵
</div>

## tasiyanc — post 5203

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
فروش بسته اس اطلاع رسانی میشه اگه باز کنیم
</div>

## tasiyanc — post 5202

<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">
javidgorz-1.0.7-universal.apk
</div>

