from src.core.app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=False para distribución, True para desarrollo
    app.run(host='127.0.0.1', port=5000, debug=True)