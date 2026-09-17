except Exception as error:
        print(
            "VIDEO WORKER ERROR:",
            repr(error)
        )

        try:
            send_message(
                chat_id,
                "تعذر إنشاء الفيديو حاليًا. "
                "قد يكون النموذج غير متاح أو لا يوجد رصيد كافٍ."
            )
        except Exception as send_error:
            print(
                "VIDEO ERROR MESSAGE FAILED:",
                repr(send_error)
            )


# =========================
# Flask routes
# =========================

@app.route("/", methods=["GET"])
def home():
    return "Sila Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(
        silent=True
    ) or {}

    message = data.get(
        "message",
        {}
    )

    chat = message.get(
        "chat",
        {}
    )

    text = message.get("text")

    if not chat:
        return "OK", 200

    chat_id = chat.get("id")

    if not chat_id:
        return "OK", 200

    if not text:
        send_message(
            chat_id,
            "أستطيع حاليًا التعامل مع النص. "
            "أضيفي لي صورة أو ملفًا لاحقًا."
        )

        return "OK", 200

    text = text.strip()

    # Media request
    media_type, prompt = detect_media_request(
        text
    )

    if media_type == "image":

        if not prompt:
            send_message(
                chat_id,
                "🎨 اكتبي وصف الصورة.\n\n"
                "مثال:\n"
                "/image قطة بيضاء في مدينة مستقبلية ليلًا"
            )

            return "OK", 200

        threading.Thread(
            target=image_worker,
            args=(chat_id, prompt),
            daemon=True
        ).start()

        return "OK", 200

    if media_type == "video":

        if not prompt:
            send_message(
                chat_id,
                "🎬 اكتبي وصف الفيديو.\n\n"
                "مثال:\n"
                "/video سيارة رياضية تسير في شارع ممطر ليلًا"
            )

            return "OK", 200

        threading.Thread(
            target=video_worker,
            args=(chat_id, prompt),
            daemon=True
        ).start()

        return "OK", 200

    # Normal AI chat
    try:

        reply = ask_ai(text)

        send_message(
            chat_id,
            reply
        )

    except Exception as error:

        print(
            "CHAT ERROR:",
            repr(error)
        )

        try:
            send_message(
                chat_id,
                "عذرًا، حدث خطأ مؤقتًا. "
                "حاولي إرسال رسالتك مرة أخرى."
            )

        except Exception as send_error:

            print(
                "CHAT ERROR MESSAGE FAILED:",
                repr(send_error)
            )

    return "OK", 200


# =========================
# Start server
# =========================

if name == "main":
    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
