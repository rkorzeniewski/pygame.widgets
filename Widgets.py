#-*- coding: UTF-8 -*-
import pygame
from pygame.locals import *

class Widget:
   def __init__(self, x, y, w=0, h=0):
      """ 
      Parametry:
         show - oznacza czy mamy wyswietlac widget czy nie 
         enabled - oznacza czy widget jest wlaczony i obsługuje zdarzenia czy nie
         initialized - oznacza czy widget zostal juz zbudowany i zainicjalizowany
                       jesli tak to moze obslugiwac zdarzenia i byc wyswietlany
                       w zaleznosci od parametrow enabled i show
         modal - wskazuje ze widget powinien w pierwszej kolejnosci odbierac
                 zdarzenia bez wzgledu na to czy mysz jest w zasiegu widgetu czy nie
                 to takze umozliwia przekierowanie klawiatury do odpowiedniego widgetu
                 i obsluge wlasciwosci select/focus
         rect - koordynaty wyswietlanego widgetu wzgledem ekranu na ktorym jest wyswietlany
         screen - ekran na ktorym jest rysowany widget
         surface - obrazek widgeta do wyswietlenia
      Metody:
         setenabled - ustawia flage enabled
         setshow - ustawia flage show
         setmodal - ustawia flage modal
         setscreen - ustawia ekran na ktorym jest rysowany widget,
                     opcjalnalny parametr shared=1 powoduje stworzenie wspoldzielonego
                     surface i przypisane go do widgetu
      Wirtualne:
         setinitialized - do obslugi zainicjalizowania widgetu
      """
      self.show = 0
      self.enabled = 1
      self.initialized = 0
      self.modal = 0
      self.rect = pygame.Rect(x,y,w,h)
      if w != 0 and h != 0:
         self.surface = pygame.Surface((w,h))
      else:
         self.surface = None
      self.screen = None

   def __repr__(self):
       return "<Widget: enabled:"+str(self.enabled)+" show:"+str(self.show)+" init:"+str(self.initialized)+" modal:"+str(self.modal)+" rect("+str(self.rect.x)+","+str(self.rect.y)+","+str(self.rect.w)+","+str(self.rect.h)+") "+str(self.surface)+">"

   def setenabled(self,ena):
      self.enabled = ena

   def setshow(self,s):
      self.show = s

   def setinitialized(self):
      pass

   def setmodal(self,modal):
      self.modal = modal

   def setscreen(self,screen,shared=0):
      self.screen = screen
      if shared == 1:
         self.surface = self.screen.subsurface(self.rect)

   def draw(self,ip=1):
      if self.initialized == 1 and self.show == 1:
         self.update(ip)
         if ip == 1 and self.surface != None:
            if self.surface.get_parent() == None and self.screen != None:
               self.screen.blit(self.surface,self.rect)
         else:
            return self.surface

   def mouse(self,(x,y),(b1,b3,b2)):
      pass

   def keyboard(self,event):
      pass

   def domouse(self,(x,y),(b1,b3,b2)):
      if self.rect.collidepoint(x,y) or self.modal == 1:
         self.mouse((x,y),(b1,b3,b2))
         return True
      else:
         return False

   def dokeyboard(self,event):
      if self.modal == 1:
         self.keyboard(event)
         return True
      else:
         return False

   def update(self,ip=1):
      pass

   def event(self,event):
      if self.initialized == 1 and self.enabled == 1:
         if event.type == KEYDOWN or event.type == KEYUP:
            return self.dokeyboard(event)
         elif event.type == MOUSEMOTION:
            return self.domouse(event.pos,event.buttons)
         elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
               buttons = (1,0,0)
            elif event.button == 2:
               buttons = (0,1,0)
            elif event.button == 3:
               buttons = (0,0,1)
            return self.domouse(event.pos,buttons)
         elif event.type == MOUSEBUTTONUP:
            buttons = (0,0,0)
            return self.domouse(event.pos,buttons)

   def proc(self,events=0):
      pass

class Events:
   def __init__(self,screen=None):
      self.screen = screen
      self.objects = []

   def add(self,widget,init=1,scr=1):
      self.objects.append(widget)
      if scr == 1 and self.screen != None:
         widget.setscreen(self.screen)
      if init == 1:
         widget.setinitialized()

   def remove(self,widget):
      self.objects.remove(widget)

   def getobjects(self):
      return self.objects

   def draw(self):
      for a in self.objects:
         a.draw()

   def focus(self,widget):
      i = self.objects.index(widget)
      if widget.modal == 1 and i > 0:
         # obiekt modalny na poczatek
         b = self.objects[0]
         self.objects[0] = widget
         self.objects[i] = b

   def event(self,event):
      #print event
      for a in self.objects:
         if a.event(event):
            self.focus(a)
            return True
      return False

class Button (Widget):
   def __init__(self, x, y, w=0, h=0, tex0=None, tex1=None, tex2=None):
      """
         state - status klawisza:
            0 - klawisz off
            1 - klawisz on
            2 - klawisz disabled
         textures[$state]
      """
      Widget.__init__(self,x,y,w,h)
      self.state = 0
      self.textures = [None,None,None]
      if tex0 != None:
         self.set_texture(tex0,0)
      if tex1 != None:
         self.set_texture(tex1,1)
         if self.rect.w == 0 or self.rect.h == 0:
            self.rect.w = self.textures[1].get_width()
            self.rect.h = self.textures[1].get_height()
      if tex2 != None:
         self.set_texture(tex2,2)

   def setenabled(self,ena):
      self.enabled = ena
      if ena == 0:
         self.state = 2
      elif self.state == 2:
         self.state = 0

   def setinitialized(self):
      if self.textures[2] == None:
         self.set_dis_texture()
      self.initialized = 1
      self.show = 1

   def set_texture(self,imagefile,tex):
      self.textures[tex] = pygame.image.load(imagefile)

   def set_dis_texture(self):
      self.textures[2] = self.textures[1].copy()
      self.textures[2].fill((255,127,5),None,BLEND_MULT)
      self.rect.w = self.textures[1].get_width()
      self.rect.h = self.textures[1].get_height()

   def set_on_texture(self,imagefile):
      self.set_texture(imagefile,1)
      self.set_dis_texture()

   def set_off_texture(self,imagefile):
      self.set_texture(imagefile,0)

   def update(self,ip=1):
      self.surface = self.textures[self.state]

class PushButton(Button):
   def __init__(self, x, y, w=0, h=0, tex0=None, tex1=None, tex2=None):
      Button.__init__(self,x,y,w,h,tex0,tex1,tex2)
      self.pushed = 0

   def mouse(self,(x,y),(b1,b3,b2)):
      if b1 == 1 and self.pushed == 0:
         self.pushed = 1
         self.state = 1
         self.setmodal(1)
         self.proc()
      elif b1 == 0 and self.pushed == 1:
         self.pushed = 0
         self.state = 0
         self.setmodal(0)
         self.proc()

class ToggleButton(Button):
   def __init__(self, x, y, w=0, h=0, tex0=None, tex1=None, tex2=None):
      Button.__init__(self,x,y,w,h,tex0,tex1,tex2)
      self.toggle = 0
      self.push = 0

   def mouse(self,(x,y),(b1,b3,b2)):
      if b1 == 1 and self.push == 0:
         self.push = 1
         self.toggle = 1 - self.toggle
         self.state = self.toggle
         self.proc()
      elif b1 == 0 and self.push == 1:
         self.push = 0

class ProgressBar(Widget):
   def __init__(self, x, y, w=0, h=0):
      Widget.__init__(self,x,y,w,h)
      self.progress = 0.0
      self.background = (128,128,128)
      self.barcolor = (0,0,255)

   def setprogress(self,progress):
      self.progress = progress

   def setbackground(self,(c1,c2,c3)):
      self.background = (c1,c2,c3)

   def setbackground(self,(c1,c2,c3)):
      self.background = (c1,c2,c3)

   def setinitialized(self):
      self.initialized = 1
      self.show = 1

   def update(self,ip=1):
      self.surface.fill(self.background)
      r=Rect(1,1,(self.rect.w-2)*self.progress/100.0,self.rect.h-2)
      pygame.draw.rect(self.surface, self.barcolor, r)

class InputBar(Widget):
   def __init__(self, x, y, w=8, h=8, text=""):
      Widget.__init__(self,x,y,w,h)
      self.background = (128,128,128)
      self.border = 1
      self.textcolor = (255,255,255)
      self.cursorcolor = (255,255,255)
      self.cursorpos = 0
      self.cursorx = 0
      self.cursorticks = 0
      self.cursordraw = 0
      self.push = 0
      self.fromstr(text)
      self.font = pygame.font.SysFont("Arial",h/2)
      self.stxt = None
      self.smetr = None

   def setinitialized(self):
      self.initialized = 1
      self.show = 1

   def tostr(self):
      b=u""
      for a in self.text:
         b+=a
      return b

   def fromstr(self,text):
      self.text = []
      for a in text:
         self.text.append(a)

   def update(self,ip=1):
      if self.border > 0:
         self.surface.fill((0,0,0))
      r=Rect(0,0,self.rect.w,self.rect.h)
      pygame.draw.rect(self.surface, self.background, r, self.border)
      if self.stxt != None:
         self.surface.blit(self.stxt,(self.border+2,1))
      if self.modal == 1:
         self.cursorticks = (self.cursorticks+1) % 20
         if self.cursorticks == 0:
            self.cursordraw = 1 - self.cursordraw
         if self.cursordraw == 1:
            x = self.cursorx + self.border + 2
            y1 = self.border + 1
            y2 = self.rect.h - self.border - 2
            pygame.draw.line(self.surface,self.cursorcolor,(x,y1),(x,y2))

   def setcursorx(self):
      s=0
      for a in self.smetr[:self.cursorpos]:
         (t1,t2,t3,t4,s1) = a
         s+=s1
      self.cursorx = s
      #print self.cursorpos,self.cursorx

   def render(self):
      #print self.cursorpos,self.text
      t = self.tostr()
      if len(self.text) > 0:
         self.smetr = self.font.metrics(t)
         self.setcursorx()
         self.stxt = self.font.render("%s"%t,True,(255,255,255))
      else:
         self.smetr = None
         self.cursorx = 0
         self.stxt = None

   def mouse(self, (x,y), (b1,b3,b2)):
      if b1 == 1 and self.push == 0:
         # wcisniecie klawisza
         self.push = 1
         if self.modal == 0:
            self.setmodal(1)
         elif self.rect.collidepoint((x,y)) == False:
            if self.modal == 1:
               self.setmodal(0)
               self.push = 0
      elif b1 == 0 and self.push == 1:
         # zwolnienie klawisza
         self.push = 0

   def keyboard(self,event):
      if event.type == KEYDOWN:
         #print "Key pressed:"+str(event.key)+" u'"+event.unicode+"'"
         if event.key == 13:
            # zakonczenie wprowadzania
            self.setmodal(0)
            self.push = 0
            self.proc()
         elif event.key == 27:
            # anulowanie wprowadzania
            self.setmodal(0)
            self.push = 0
         elif event.key == 8:
            # kasuj ostatni znak
            if self.cursorpos > 0:
               #print "Delete"
               self.text = self.text[:self.cursorpos-1]+self.text[self.cursorpos:]
               self.cursorpos -= 1
               self.render()
         elif event.key == 275:
            # prawo
            if self.cursorpos < len(self.text):
               #print "Prawo"
               self.cursorpos += 1
               self.setcursorx()
         elif event.key == 276:
            # lewo
            if self.cursorpos > 0:
               #print "Lewo"
               self.cursorpos -= 1
               self.setcursorx()
         elif event.key == 278:
            # home
            if self.cursorpos > 0:
               #print "Home"
               self.cursorpos = 0
               self.setcursorx()
         elif event.key == 279:
            # end
            if self.cursorpos < len(self.text):
               #print "End"
               self.cursorpos = len(self.text)
               self.setcursorx()
         elif event.unicode.isalnum() or event.unicode == u' ':
            # znaki alfanumeryczne
            self.text.insert(self.cursorpos,event.unicode)
            self.cursorpos+=1
            self.render()
         return True
      return False
