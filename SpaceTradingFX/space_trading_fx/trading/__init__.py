try:
    import PySimpleGUI as sg
except Exception:
    # Provide a minimal stub so the package can be imported in headless/test environments
    class _DummyWindow:
        def __init__(self, *a, **k):
            pass

        def Read(self):
            return (None, {})

        def close(self):
            pass

    class _SG:
        Text = staticmethod(lambda *a, **k: None)
        Button = staticmethod(lambda *a, **k: None)
        Combo = staticmethod(lambda *a, **k: None)
        Window = _DummyWindow

    sg = _SG()


def Dispaly_candelstick(window,API,candlestick):
    
    layout = [[sg.Text("Select: "), sg.text(candlestick, key="candlestick")],
              [sg.Text("Value"), sg.Text(API.get_candles(candlestick)[-1]["close"],key="value")],
              [sg.Button("Ok")]
              ]
    
    window = sg.Window("Details and candlestick",layout,keep_on_top=True)
    
    
    while True:
        event,values = window.Read()
        
        if event in (None,"Ok"):
            break
        
        window.close()
        
        return values
    
    
def Display_Details(window, API, candlestick):
    layout = [
        [sg.Text('Paridade:'), sg.Text(candlestick, key='candlestick')],
        [sg.Text('Valor atual:'), sg.Text(API.get_candles(candlestick)[-1]['close'], key='valor')],
        [sg.Button('Ok')]
    ]
    window = sg.Window('Details and candlestick', layout, keep_on_top=True)

    while True:
        event, values = window.Read()

        if event in (None, 'Ok'):
            break

    window.close()    
    
def Display_Speed(window, API):
    layout = [
        [sg.Text("Select one speed: "),sg.Combo(API.speed(), key="speed", size=(20,None))],
        [sg.Button('Ok'), sg.Button('Cancel')]
        ]
       
    window = sg.Window('SPEED', layout, keep_on_top=True)

    while True:
        event, values = window.Read()

        if event in (None, 'Cancel'):
            break

        if event == 'Ok':
            break

    window.close()

    return values

def Display_Details_speed(window, API, speed, values):
    layout = [
        [sg.Text('Speed:'), sg.Text(speed, key='speed')],
        [sg.Button('Ok')]
    ]
    window = sg.Window('Details and speed', layout, keep_on_top=True)

    while True:
        event, values = window.Read()

        if event in (None, 'Ok'):
            break

    window.close()
    
    speed_details = API.get_speed_details(speed)
    for detail, value in speed_details.items():
        print(f"{detail}: {value}")
    
    return values

class MockAPI:
    def paridades(self):
        return ["EUR/USD", "GBP/USD", "USD/JPY", "AUDJPY"]
    
    def get_candles(self, candlestick):
        return [{"close": 1.1234}]
    
    def speed(self):
        return ["1x", "2x", "3x"]
    
    def get_speed_details(self, speed):
        return {"description": f"Speed set to {speed}", "max_limit": 100}
    

def main(API):
    layout = [
        [sg.Text("Welcome to the Application")],
        [sg.Button("Select Paridade"), sg.Button("Select Speed")],
        [sg.Button("Exit")]
    ]
    
    window = sg.Window("Main Application", layout, keep_on_top=True)

    while True:
        event, values = window.Read()

        if event in (None, "Exit"):
            break

        if event == "Select Paridade":
            candlesticks_values = Dispaly_candelstick(window, API)
            if 'candlestick' in candlesticks_values:
                candlestick = candlesticks_values['candlestick']
                Display_Details(window, API, candlestick)

        if event == "Select Speed":
            speed_values = Display_Speed(window, API)
            if 'speed' in speed_values:
                speed = speed_values['speed']
                Display_Details_speed(window, API, speed, speed_values)

    window.close()
    return values

# Run the Application
if __name__ == "__main__":
    api_instance = MockAPI()
    main(api_instance)