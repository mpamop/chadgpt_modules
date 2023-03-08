import logging 
import io 
 
from telethon import TelegramClient, events, sync 
from telethon.sessions import StringSession 
 
from .. import loader, utils 
 
logger = logging.getLogger(__name__) 
 
 
@loader.tds 
class SaveSessionMod(loader.Module): 
    """Сохранение сессии в файл, загрузка её из файла и отправление сессии""" 
    strings = {"name": "SaveSession"} 
 
    async def client_ready(self, client, db): 
        self.client = client 
        self.db = db 
 
    async def savesscmd(self, message): 
        """Сохранить текущую сессию""" 
        session_string = StringSession.save(self.client.session) 
        self.db.set("friendly-telegram", "saved_session", session_string) 
        await utils.answer(message, "Текущая сессия сохранена!") 
 
    async def loadsscmd(self, message): 
        """Загрузить ранее сохраненную сессию""" 
        saved_session = self.db.get("friendly-telegram", "saved_session", None) 
        if not saved_session: 
            await utils.answer(message, "Ранее не было сохранено ни одной сессии.") 
            return 
 
        session = StringSession(saved_session) 
        client = TelegramClient(session, self.client.api_id, self.client.api_hash) 
        await client.connect() 
 
        if not await client.is_user_authorized(): 
            await utils.answer(message, "Эта сессия не действительна или её создал другой пользователь.") 
            return 
 
        self.client.session = session 
        await self.client.connect() 
 
        await utils.answer(message, "Сессия успешно загружена!") 
 
    async def sendsscmd(self, message): 
        """Отправить сохраненную сессию другому пользователю""" 
        saved_session = self.db.get("friendly-telegram", "saved_session", None) 
        if not saved_session: 
            await utils.answer(message, "Ранее не было сохранено ни одной сессии.") 
            return 
  
        if len(message.text.split()) < 2: 
            to_user = message.peer_id 
            text = f"Сессия успешно отправлена в этот чат!" 
        else:
            to_user = message.text.split()[1] 
            text = f"Сессия успешно отправлена пользователю {to_user}!" 
  
        me = await self.client.get_me()
        phone_number = me.phone
        filename = f"{phone_number}.txt" 
  
        session_file = io.BytesIO(saved_session.encode()) 
        session_file.name = filename 
  
        async with self.client.conversation(to_user) as conv: 
            response = await conv.send_file(session_file, caption=filename) 
  
        await utils.answer(message, text)