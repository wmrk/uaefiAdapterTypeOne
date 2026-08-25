import pcbnew
from pcbnew import *

def route_board():
    board = pcbnew.GetBoard()
    
    # 1. Удаляем все существующие дорожки и vias
    for t in list(board.GetTracks()):
        board.Remove(t)
    
    # 2. Силовые цепи (широкие дорожки 0.8мм)
    power_nets = ["GND", "+12V", "+5VP", "GNDA", "/12V_KEY_VIGN"]
    
    # 3. Получаем список цепей через NetInfo (KiCad 8+)
    netinfo = board.GetNetInfo()
    
    # Итерируемся по всем цепям
    for net in netinfo.Nets():
        net_name = net.GetNetname()
        net_code = net.GetNet()
        
        # Пропускаем не подключённые цепи
        if net_name.startswith("unconnected-") or net_name == "" or net_name is None:
            continue
        
        # Получаем пады этой цепи
        pads = board.GetPadsByNet(net_code)
        
        if len(pads) < 2:
            continue
        
        is_power = net_name in power_nets
        width = 800000 if is_power else 254000  # 0.8mm or 0.254mm
        
        start_pad = pads[0]
        start_pos = start_pad.GetPosition()
        start_layer = start_pad.GetLayer()
        
        for i in range(1, len(pads)):
            end_pad = pads[i]
            end_pos = end_pad.GetPosition()
            end_layer = end_pad.GetLayer()
            
            if start_layer == end_layer:
                # Прямая дорожка на одном слое
                track = PCB_TRACK(board)
                track.SetStart(start_pos)
                track.SetEnd(end_pos)
                track.SetWidth(width)
                track.SetLayer(start_layer)
                track.SetNet(net_code)
                board.Add(track)
            else:
                # Ломаная дорожка с Via
                mid_x = (start_pos.x + end_pos.x) / 2
                mid_y = (start_pos.y + end_pos.y) / 2
                mid_pos = wxPoint(int(mid_x), int(mid_y))
                
                # Сегмент 1
                t1 = PCB_TRACK(board)
                t1.SetStart(start_pos)
                t1.SetEnd(mid_pos)
                t1.SetWidth(width)
                t1.SetLayer(start_layer)
                t1.SetNet(net_code)
                board.Add(t1)
                
                # Via
                via = PCB_VIA(board)
                via.SetPosition(mid_pos)
                via.SetWidth(width)
                via.SetViaType(VIA_THROUGH)
                via.SetNet(net_code)
                board.Add(via)
                
                # Сегмент 2
                t2 = PCB_TRACK(board)
                t2.SetStart(mid_pos)
                t2.SetEnd(end_pos)
                t2.SetWidth(width)
                t2.SetLayer(end_layer)
                t2.SetNet(net_code)
                board.Add(t2)
    
    pcbnew.Refresh()
    print("Трассировка завершена! Запустите DRC.")

route_board()