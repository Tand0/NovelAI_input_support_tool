#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    NovelAI input support tool
"""
import tkinter
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image

import json
import re
import random


class ButtonTextFrame():

    _text = None

    _frontPage = None

    _not_ignore = None

    def __init__(self, frontPage, tab_text, not_ignore):
        self._frontPage = frontPage
        self._not_ignore = not_ignore

        tab_frame = tkinter.Frame(tab_text, borderwidth=5)
        if not_ignore:
            tab_frame.pack(side=tkinter.TOP, fill=tkinter.X, expand=0)
        else:
            tab_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X, expand=0)

        # tab_text
        self._text = tkinter.Text(tab_frame)
        self._text.insert(1.0, "")
        self._text.pack(fill=tkinter.BOTH)

        # tab_text
        frame = tkinter.Frame(tab_frame)
        frame.pack(side=tkinter.BOTTOM, fill=tkinter.X, expand=0)
        button_bottom = tkinter.Button(
            frame,
            text="To tree",
            command=self.click_to_tree)
        button_bottom.grid(row=0, column=0)
        button_bottom = tkinter.Button(
            frame,
            text="From tree",
            command=self.click_from_tree)
        button_bottom.grid(row=0, column=2)
        button_bottom = tkinter.Button(
            frame,
            text="Past",
            command=self.click_past)
        button_bottom.grid(row=1, column=0)
        button_bottom = tkinter.Button(
            frame,
            text="Copy",
            command=self.click_copy)
        button_bottom.grid(row=1, column=2)

    def get_text(self):
        return self._text.get("1.0", "end")

    def set_text(self, ans):
        self._text.delete(0., tkinter.END)
        self._text.insert(1.0, ans)

    def click_to_tree(self):
        result = self._text.get("1.0", "end")
        result = self._frontPage.create_data(result, self._not_ignore)
        self._frontPage.load_child("", result)

    def click_from_tree(self):
        result = self._frontPage.get_child_data("")
        result = self._frontPage.remove_ignore(result, self._not_ignore)
        result = self._frontPage.dict_to_list(result)
        if 0 < len(result):
            result = ', '.join(result)
            self._text.delete(0., tkinter.END)
            self._text.insert(1.0, result)

    def click_copy(self):
        result = self.get_text()
        self._frontPage.get_main().clipboard_clear()
        self._frontPage.get_main().clipboard_append(result)

    def click_past(self):
        ans = self._frontPage.get_main().clipboard_get()
        self.set_text(ans)


class FrontPage():

    _main = None
    _table = None
    _tree = None
    _entry = None
    _image_text = None
    _btf_top = None
    _btf_bottom = None
    _combobox = None

    TEXT_IGNORE = "Ignore-"
    TEXT_UC = "uc-"
    TEXT_SEQENCE = "Sequence"
    TEXT_SELECT = "Select"
    TEXT_WORD = "word"
    TEXT_WEIGHT = "Weight"
    FILE_DATA = "data.json"

    TAG_BLACK = "black"
    TAG_RED = "red"
    TAG_BLUE = "blue"
    TAG_GRAY = "gray_"

    def get_main(self):
        return self._main

    def __init__(self):
        self._main = tkinter.Tk()
        self._main.geometry("400x800")
        self._main.title(u"Tekitou")
        notebook = ttk.Notebook(self._main)

        #
        tab_text = tkinter.Frame(notebook, bg='white', borderwidth=5)
        tab_tree = tkinter.Frame(notebook, bg='white', borderwidth=5)
        tab_image = tkinter.Frame(notebook, bg='white', borderwidth=5)

        #
        tab_text.pack(fill=tkinter.BOTH)
        tab_tree.pack(fill=tkinter.BOTH)
        tab_image.pack(fill=tkinter.BOTH)
        #
        notebook.add(tab_image, text="image")
        notebook.add(tab_text, text="text")
        notebook.add(tab_tree, text="tree")

        #
        self._btf_top = ButtonTextFrame(self, tab_text, True)
        self._btf_bottom = ButtonTextFrame(self, tab_text, False)

        #
        # tab_tree
        frame = tkinter.Frame(tab_tree)
        frame.pack(side=tkinter.TOP, fill=tkinter.X, expand=0)
        button_bottom = tkinter.Button(
            frame,
            text="Save",
            command=self.click_save)
        button_bottom.grid(row=0, column=0)
        button_bottom = tkinter.Button(
            frame,
            text="Load",
            command=self.click_load)
        button_bottom.grid(row=0, column=1)

        # tab_tree
        column = ("Name")
        self._tree = ttk.Treeview(
            tab_tree,
            show=['tree', 'headings'],
            height=20,
            columns=column)
        self._tree.pack(fill=tkinter.BOTH, expand=1)
        self._tree.column('#0', width=30)
        self._tree.column('Name', width=80)
        self._tree.heading("#0", text="Layer")
        self._tree.heading("Name", text="Name")
        self._tree.tag_configure(self.TAG_BLACK, foreground='black')
        self._tree.tag_configure(self.TAG_RED, foreground='red')
        self._tree.tag_configure(self.TAG_BLUE, foreground='blue')
        self._tree.tag_configure(
            self.TAG_GRAY + self.TAG_BLACK,
            foreground='black', background='gray')
        self._tree.tag_configure(
            self.TAG_GRAY + self.TAG_RED,
            foreground='red', background='gray')
        self._tree.tag_configure(
            self.TAG_GRAY + self.TAG_BLUE,
            foreground='blue', background='gray')
        self._tree.bind("<<TreeviewSelect>>", self.select_record)
        #
        frame = tkinter.Frame(tab_tree)
        frame.pack(side=tkinter.BOTTOM, fill=tkinter.X, expand=0)
        button_bottom = tkinter.Button(
            frame,
            text="Up",
            command=self.click_up)
        button_bottom.grid(row=0, column=0)
        button_bottom = tkinter.Button(
            frame,
            text="Down",
            command=self.click_down)
        button_bottom.grid(row=0, column=1)
        button_bottom = tkinter.Button(
            frame,
            text="Enhance",
            command=self.click_enhance)
        button_bottom.grid(row=0, column=2)
        button_bottom = tkinter.Button(
            frame,
            text="Not Enhance",
            command=self.click_not_enhance)
        button_bottom.grid(row=0, column=3)
        #
        button_bottom = tkinter.Button(
            frame,
            text="Cut Tree",
            command=self.click_button_cut)
        button_bottom.grid(row=2, column=0)
        #
        button_bottom = tkinter.Button(
            frame,
            text="Past Tree",
            command=self.click_button_past)
        button_bottom.grid(row=2, column=1)
        #
        button_bottom = tkinter.Button(
            frame,
            text="Ignore",
            command=self.click_ignore)
        button_bottom.grid(row=2, column=3)
        #
        self._entry = tkinter.Entry(frame)
        self._entry.grid(row=3, column=0)
        button_bottom = tkinter.Button(
            frame,
            text="Insert Word",
            command=self.click_insert)
        button_bottom.grid(row=3, column=1)
        button_bottom = tkinter.Button(
            frame,
            text="Change Word",
            command=self.click_change)
        button_bottom.grid(row=3, column=2)
        #
        button_bottom = tkinter.Button(
            frame,
            text="Copy Word",
            command=self.click_button_word_copy)
        button_bottom.grid(row=4, column=1)
        #
        button_bottom = tkinter.Button(
            frame,
            text="Past Word",
            command=self.click_button_word_past)
        button_bottom.grid(row=4, column=2)
        #
        module = (self.TEXT_SEQENCE, self.TEXT_SELECT, self.TEXT_WEIGHT)
        self._combobox = ttk.Combobox(frame, values=module)
        self._combobox.grid(row=5, column=0)
        button_bottom = tkinter.Button(
            frame,
            text="Insert Tree",
            command=self.click_combobox)
        button_bottom.grid(row=5, column=1)
        #
        # tab_image
        self._image_text = tkinter.Text(tab_image, borderwidth=5)
        self._image_text.insert(1.0, "PNG image data...")
        self._image_text.pack(fill=tkinter.BOTH, expand=1)
        button_bottom = tkinter.Button(
            tab_image,
            text="Load Image",
            command=self.click_image_load)
        button_bottom.pack(side=tkinter.BOTTOM, fill=tkinter.X, expand=0)
        #
        #
        # all update
        self.click_load()
        notebook.pack(fill=tkinter.BOTH)

    def main(self):
        self._main.mainloop()

    def create_data(self, string, not_ignore):
        middle = string
        middle = string.replace("\"", ",").replace("_", " ").replace(
            "(", "{").replace(")", "}").replace(
            "+", ",").replace(
            "|", ",").replace("\r", ",").replace(
            "\n", ",").split(',')
        top_text = self.TEXT_SEQENCE
        word_text = self.TEXT_WORD
        values = "prompt"
        if not not_ignore:
            top_text = self.TEXT_UC + top_text
            word_text = self.TEXT_UC + word_text
            values = "uc"
        top = {"text": top_text, "values": values, "child": []}
        for name in middle:
            name = self.create_name(name)
            if name == "":
                continue
            name = {"text": word_text, "values": name, "child": []}
            top["child"].append(name)
        return top

    def create_name(self, name):
        name = name.strip()
        name = re.sub(r"\s+", " ", name)
        pos = self.get_enhance_pos(name)
        name = self.get_enhance_text(name, pos)
        name_raw = name.replace("{", "").replace("}", "").replace(
            "[", "").replace("]", "").strip()
        name_raw = re.sub(r"\s+", " ", name_raw).strip()
        pattern = r'(.*)\s*[\s:](\d+(\.\d+)?)\s*$'
        result = re.search(pattern, name_raw)
        if result:
            name = result.group(1)
            pos = float(result.group(2))
            now = 1.0
            if pos < 1.0:
                for _ in range(10):
                    name = "[" + name + "]"
                    now = now / 1.1
                    if now < pos:
                        break
            else:
                for _ in range(10):
                    name = "{" + name + "}"
                    now = now * 1.1
                    if now > pos:
                        break
        else:
            name = name.replace(":", " ").strip()
        return name

    def select_record(self, _):
        record_id = self._tree.focus()
        record_values = self._tree.item(record_id, 'values')
        if isinstance(record_values, tuple):
            record_values = record_values[0]
        if record_values == "":
            return
        self._entry.delete(0, tkinter.END)
        self._entry.insert(0, record_values)

    _cut = None

    def click_button_cut(self):
        record_id = self._tree.focus()
        if "" == record_id:
            return
        #
        self._cut = self.get_child_data(record_id)
        # print(self._cut)
        #
        self._tree.delete(record_id)
        if len(self._tree.get_children("")) == 0:
            self._token_list = []

    def click_button_past(self):
        record_id = self._tree.focus()
        if self._cut is None:
            return
        #
        if "" != record_id:
            text = self._tree.item(record_id, 'text')
            if self.TEXT_WORD in text:
                record_id = self._tree.parent(record_id)
        self.load_child(record_id, self._cut)
        #
        self._cut = None

    def click_change(self):
        record_id = self._tree.focus()
        new_values = self._entry.get()
        self._tree.item(record_id, values="\"" + new_values + "\"")

    def click_insert(self):
        name = self._entry.get()
        name = self.create_name(name)
        self.create_folder(self.TEXT_WORD, name)

    def click_button_word_copy(self):
        name = self._entry.get()
        self._main.clipboard_clear()
        self._main.clipboard_append(name)

    def click_button_word_past(self):
        name = self._main.clipboard_get()
        self._entry.delete(0, tkinter.END)
        self._entry.insert(0, name)

    def click_combobox(self):
        text = self._combobox.get()
        if text in (self.TEXT_SELECT, self.TEXT_WEIGHT, self.TEXT_SEQENCE):
            self.create_folder(text, "")
        else:
            self.create_folder(self.TEXT_SEQENCE, "")

    def create_folder(self, text, name):
        if self.TEXT_WORD in text:
            tags = self.TAG_GRAY
        else:
            tags = self.TAG_BLUE
        #
        record_id = self._tree.focus()
        if record_id == "":
            record_text = self.TEXT_WORD
        else:
            record_text = self._tree.item(record_id, 'text')
        #
        if self.TEXT_WORD in record_text:
            if record_id == "":
                parent_iid = ""
                index = 0
                tags = self.TAG_BLUE
            else:
                parent_iid = self._tree.parent(record_id)
                index = self._tree.index(record_id)
                record_text = self._tree.item(parent_iid, 'text')
                if self.TEXT_UC in record_text:
                    text = self.TEXT_UC + text
                    tags = self.TAG_GRAY + tags
            self._tree.insert(
                parent=parent_iid,
                index=index,
                text=text,
                tags=tags,
                values="\"" + name + "\"")
        else:
            if self.TEXT_UC in record_text:
                text = self.TEXT_UC + text
                tags = self.TAG_GRAY + tags
            self._tree.insert(
                parent=record_id,
                index=0,
                text=text,
                tags=tags,
                values="\"" + name + "\"")

    def click_up(self):
        now = self._tree.focus()
        child = now
        if "" == child:
            return
        parent = self._tree.parent(child)
        index = self._tree.index(child)
        if index == 0:
            if "" == parent:
                return
            child = parent
            parent = self._tree.parent(child)
            index = self._tree.index(child)
            self._tree.move(parent=parent, index=index, item=now)
            return
        childlen = self._tree.get_children(parent)
        target = childlen[index - 1]
        index = self._tree.index(target)
        text = self._tree.item(target, 'text')
        if self.TEXT_WORD in text:
            self._tree.move(parent=parent, index=index, item=now)
            return
        parent = target
        childlen = self._tree.get_children(target)
        self._tree.move(parent=parent, index="end", item=now)

    def click_down(self):
        now = self._tree.focus()
        child = now
        if "" == child:
            return
        parent = self._tree.parent(child)
        index = self._tree.index(child) + 1
        childlen = self._tree.get_children(parent)
        if index < len(childlen):
            target = childlen[index]
            text = self._tree.item(target, 'text')
            if self.TEXT_WORD in text:
                self._tree.move(parent=parent, index=index, item=now)
                return
            self._tree.move(parent=target, index=0, item=now)
            return
        child = parent
        if "" == child:
            return
        parent = self._tree.parent(child)
        index = self._tree.index(child) + 1
        childlen = self._tree.get_children(parent)
        if index < len(childlen):
            target = childlen[index]
            text = self._tree.item(target, 'text')
            self._tree.move(parent=parent, index=index, item=now)
            return
        self._tree.move(parent=parent, index="end", item=now)

    def click_ignore(self):
        record_id = self._tree.focus()
        record_text = self._tree.item(record_id, 'text')
        if self.TEXT_IGNORE in record_text:
            record_text = record_text.replace(self.TEXT_IGNORE, "")
        else:
            record_text = self.TEXT_IGNORE + record_text
        self._tree.item(record_id, text=record_text)

    def click_save(self):
        parent = self._tree.get_children("")
        dict = self.get_child_data(parent)
        enc = json.dumps(dict, indent=2)
        try:
            with open(self.FILE_DATA, 'wt', encoding='UTF-8') as f:
                f.write(enc)
            _ = messagebox.showinfo("Save", "OK")
        except OSError:
            _ = messagebox.showerror("Save", "NG")

    def get_child_data(self, parent):
        childrenList = []
        if isinstance(parent, list) or isinstance(parent, tuple):
            for child in parent:
                childrenList.append(self.get_child_data(child))
            return childrenList
        data = {}
        text = self._tree.item(parent, 'text')
        values = self._tree.item(parent, 'values')
        if isinstance(values, tuple):
            values = values[0]
        data["text"] = text
        data["values"] = values
        children = self._tree.get_children(parent)
        data["child"] = self.get_child_data(children)
        return data

    def click_load(self):
        try:
            with open(self.FILE_DATA, 'rt', encoding='UTF-8') as f:
                childlen = json.load(f)
                self.load_child("", childlen)
        except json.JSONDecodeError:
            pass
        except OSError:
            pass

    _token_list = []

    def load_child(self, tree_parent, dict_child):
        if isinstance(dict_child, list) or isinstance(dict_child, tuple):
            for child in dict_child:
                self.load_child(tree_parent, child)
            return
        #
        text = dict_child["text"]
        value = dict_child["values"]
        #
        if self.TEXT_WORD in text:
            token = value.replace("{", "").replace("}", "").replace(
                "[", "").replace("]", "").strip()
            if token in self._token_list:
                tags = self.TAG_RED
            else:
                tags = self.TAG_BLACK
                self._token_list.append(token)
        else:
            tags = self.TAG_BLUE
        if self.TEXT_UC in text:
            tags = self.TAG_GRAY + tags
        #
        new_tree = self._tree.insert(
            tree_parent,
            index="end",
            text=text,
            values="\"" + value + "\"",
            tags=tags)
        #
        self.load_child(new_tree, dict_child["child"])

    def click_image_load(self):
        type = [('NovelAI Image', '*.png')]
        file = filedialog.askopenfilename(filetypes=type)
        if file is None:
            return
        #
        with Image.open(file) as im:
            info = im.info
            if info is None:
                return
            try:
                ans = json.dumps(info, indent=2)
            except json.JSONDecodeError:
                return
            if ans is None:
                return
            if "Comment" in info:
                try:
                    json_dict = json.loads(info["Comment"])
                    if "prompt" in json_dict:
                        self._btf_top.set_text(json_dict["prompt"])
                    elif "Description" in info:
                        self._btf_top.set_text(info["Description"])
                    if "uc" in json_dict:
                        self._btf_bottom.set_text(json_dict["uc"])
                except json.decoder.JSONDecodeError:
                    pass
            elif "parameters" in info:
                parameters = info["parameters"]
                ans = (ans + "\n\n" + ("="*10) + "\n\n"
                       + parameters)
                key = "Negative prompt: "
                index = parameters.find(key)
                if 0 < index:
                    data = parameters[0:index]
                    self._btf_top.set_text(data)
                    parameters = parameters[index + len(key)+1:]
                    key = "\n"
                    index = parameters.find(key)
                    if 0 < index:
                        data = parameters[0:index]
                        self._btf_bottom.set_text(data)

            self._image_text.delete(0., tkinter.END)
            self._image_text.insert(1.0, ans)

    def click_enhance(self):
        self.enhance(+1)

    def click_not_enhance(self):
        self.enhance(-1)

    def enhance(self, value):
        record_id = self._tree.focus()
        record_values = self._tree.item(record_id, 'values')
        if isinstance(record_values, tuple):
            record_values = record_values[0]
        index = self.get_enhance_pos(record_values) + value
        new_values = self.get_enhance_text(record_values, index)
        self._tree.item(record_id, values="\"" + new_values + "\"")

    def get_enhance_pos(self, string):
        return string.count('{') - string.count('[')

    def get_enhance_text(self, string, index):
        string = string.replace("{", "")
        string = string.replace("}", "")
        string = string.replace("[", "")
        string = string.replace("]", "").strip()
        if index == 0:
            pass
        elif index < 0:
            for _ in range(0 - index):
                string = "[" + string + "]"
        else:
            for _ in range(index):
                string = "{" + string + "}"
        return string

    def remove_ignore(self, dict, not_ignore):
        if isinstance(dict, list) or isinstance(dict, tuple):
            ans = []
            for child in dict:
                result = self.remove_ignore(child, not_ignore)
                if result is not None:
                    ans.append(result)
            return ans
        text = dict["text"]
        if text != "":
            if self.TEXT_IGNORE in text:
                return None
            flag = self.TEXT_UC in text
            if flag == not_ignore:
                return None
        ans = {}
        ans["text"] = text
        ans["values"] = dict["values"]
        ans["child"] = self.remove_ignore(dict["child"], not_ignore)
        return ans

    def dict_to_list(self, dict):
        ans = []
        if dict is None:
            return ans
        if isinstance(dict, list) or isinstance(dict, tuple):
            for child in dict:
                ans.extend(self.dict_to_list(child))
            return ans
        mode = dict["text"]
        if self.TEXT_IGNORE in mode:
            pass
        elif self.TEXT_WORD in mode:
            ans.append(dict["values"])
        elif ((self.TEXT_SEQENCE in mode)
                or (mode == "")):
            ans.extend(self.dict_to_list(dict["child"]))
        elif self.TEXT_SELECT in mode:
            chidlen = dict["child"]
            max = len(chidlen)
            index = random.randrange(max)
            if 0 < max:
                ans.extend(
                    self.dict_to_list(
                        chidlen[index]))
        elif self.TEXT_WEIGHT in mode:
            chidlen = dict["child"]
            max = len(chidlen)
            if 0 < max:
                i = 0
                target = chidlen[0]
                while i < max:
                    if (random.randrange(100) < 60) or (i + 1 == max):
                        target = chidlen[i]
                        break
                    i = i + 1
                ans.extend(self.dict_to_list(target))
        return ans


if __name__ == "__main__":
    FrontPage().main()
