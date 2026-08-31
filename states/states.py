from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_product_name = State()
    waiting_for_product_category = State()
    waiting_for_product_price = State()
    waiting_for_product_description = State()
    waiting_for_product_image = State()
    waiting_for_broadcast_text = State()
    waiting_for_search_query = State()

class DesignerApplyStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_specialty = State()
    waiting_for_portfolio = State()

class CourierApplyStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_city = State()
    waiting_for_vehicle = State()
