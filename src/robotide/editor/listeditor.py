#  Copyright 2008-2009 Nokia Siemens Networks Oyj
#  
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  
#      http://www.apache.org/licenses/LICENSE-2.0
#  
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from robotide.utils import ButtonWithHandler, PopupMenu, RideEventHandler


class ListEditor(wx.Panel, RideEventHandler):
    _menu = ['Edit', 'Move Up', 'Move Down', '---', 'Delete']
    _buttons = []

    def __init__(self, parent, columns, controller):
        wx.Panel.__init__(self, parent)
        self._controller = controller
        self._selection = -1
        self._create_ui(columns, controller)
        self._make_bindings()

    def _create_ui(self, columns, data):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._list = self._create_list(columns, data)
        sizer.Add(self._list, 1, wx.EXPAND)
        sizer.Add((5,0))
        sizer.Add(self._create_buttons())
        sizer.Add((5,0))
        self.SetSizer(sizer)
        sizer.Layout()

    def _create_list(self, columns, data):
        return AutoWidthColumnList(self, columns, data)

    def _create_buttons(self):  
        sizer = wx.BoxSizer(wx.VERTICAL)
        for label in self._buttons:
            sizer.Add(ButtonWithHandler(self, label, width=120), 0, wx.ALL, 1)
        return sizer

    def _make_bindings(self):
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnEdit)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRightClick)

    def OnRightClick(self, event):
        PopupMenu(self, self._menu)

    def OnItemSelected(self, event):
        self._selection = event.GetIndex()

    def OnItemActivated(self, event):
        pass

    def OnMoveUp(self, event):
        if self._selection < 1:
            return
        self._switch_items(self._selection, self._selection-1)
        self._list.Select(self._selection-1, True)

    def OnMoveDown(self, event):
        if self._selection == self._list.GetItemCount() - 1 or self._selection == -1:
            return
        self._switch_items(self._selection+1, self._selection)
        self._list.Select(self._selection+1, True)

    def _switch_items(self, ind1, ind2):
        self._controller.swap(ind1, ind2)
        self.update_data()

    def OnDelete(self, event):
        if self._selection == -1:
            return
        self._controller.delete(self._selection)
        self.update_data()
        item_count = self._list.GetItemCount()
        if self._selection >= item_count:
            self._selection = item_count - 1
        self._list.Select(self._selection, True)

    def update_data(self):
        self._list.DeleteAllItems()
        self._list.insert_data(self._controller)

    def update_selected_item(self, data):
        self._list.update_item(self._selection, data)


class AutoWidthColumnList(wx.ListCtrl, ListCtrlAutoWidthMixin):

    def __init__(self, parent, columns, data=[]):
        wx.ListCtrl.__init__(self, parent, 
                             style=wx.LC_REPORT|wx.NO_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES)
        ListCtrlAutoWidthMixin.__init__(self)
        self._parent = parent
        self.populate(columns, data)

    def populate(self, columns, data):
        for i, name in enumerate(columns):
            self.InsertColumn(i, name)
            self.SetColumnWidth(i, 200)
        self.insert_data(data)

    def insert_data(self, data):
        for row, item in enumerate(data):
            rowdata = self._parent.get_column_values(item)
            self.InsertStringItem(row, rowdata[0])
            for i in range(1, len(rowdata)):
                data = rowdata[i] is not None and rowdata[i] or ''
                self.SetStringItem(row, i, data)

    def update_item(self, index, data):
        self.SetItemText(index, data[0])
        for col in range(1, len(data)):
            self.SetStringItem(index, col, data[col])
