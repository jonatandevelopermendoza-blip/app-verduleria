from src.app import app

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(app.config.get('PORT', 5000)),
        debug=True  # Solo para desarrollo
    )