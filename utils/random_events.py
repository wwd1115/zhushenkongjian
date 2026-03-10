import json
import os
import random
import time
from utils.display import clear_screen, print_header, print_info, print_warning, print_error, print_success, show_menu

def load_events():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(os.path.join(base_dir, "data", "events.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

EVENTS_DATA = load_events()

def trigger_random_event(player, world_id):
    world_events = EVENTS_DATA.get(world_id, [])
    if not world_events:
        print_info("此处风平浪静，没有发生特殊事件。")
        time.sleep(1)
        return
        
    event = random.choice(world_events)
    clear_screen()
    print_header("❓ 随机事件触发 ❓")
    print_warning(event["text"])
    
    options = {}
    for i, opt in enumerate(event["options"]):
        options[str(i+1)] = opt["desc"]
        
    choice = show_menu("请做出选择", options)
    
    try:
        opt_idx = int(choice) - 1
        selected_opt = event["options"][opt_idx]
        
        # 判定条件
        success = True
        if "req_stat" in selected_opt and "req_val" in selected_opt:
            req_stat = selected_opt["req_stat"]
            req_val = selected_opt["req_val"]
            player_val = getattr(player, req_stat, 0)
            if player_val < req_val:
                success = False
                
        result = selected_opt["success"] if success else selected_opt["fail"]
        
        clear_screen()
        if success:
            print_success(result["text"])
            if "reward_points" in result:
                player.points += result["reward_points"]
            if "reward_heal" in result:
                player.heal(result["reward_heal"])
            if "reward_mp" in result:
                player.restore_mp(result["reward_mp"])
        else:
            print_error(result["text"])
            if "damage" in result:
                player.take_damage(result["damage"])
                
        time.sleep(2)
    except Exception as e:
        print_error("处理事件时发生错误。")
        time.sleep(1)
