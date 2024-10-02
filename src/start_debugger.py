def start_debug_server():
    # if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
    PORT = 3001
    HOST = '0.0.0.0'
    print('start_debug_server')
    import debugpy
    debugpy.listen((HOST, PORT))
    # debugpy.wait_for_client()
    print(f'debug server --> HOST: {HOST}, PORT: {PORT}')
    # print('Attached!')