import os.path
from lxml import etree
import ebooklib
from ebooklib import epub
import tkinter as tk
from tkinter import filedialog,messagebox
from lxml import etree
import  re
import warnings
import traceback

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

coding='utf-8'
parser = etree.XMLParser(ns_clean=True,recover=True,encoding=coding)
files = []

# 选择你要合并的文件
def select_files():
    global files
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title = "选择文件",
        filetypes = (('文本文件','*.epub'),)

    )

    for file_path in file_paths:
        if file_path not in files:
            files.append(file_path)
    root.destroy()
# 对文件进行排序
def clear_files():
   files.clear()
def output(output_file,merged_epub):
    try:
        epub.write_epub(output_file, merged_epub)
        messagebox.showinfo("成功", f"合并后的 EPUB 文件已保存到 {output_file}")
    except Exception as e:
        print(e)
        messagebox.showerror("错误", f"保存文件时出错: {e}")
def findloc(charpters,loc):
    for charpter in charpters:
        if loc in charpter:
            return charpter
    return loc
def addtoc(item,chapters,toc):
    lxml_content = item.get_content()
    tree = etree.fromstring(lxml_content, parser)
    title_elements = tree.findall('.//{http://www.w3.org/1999/xhtml}a')
    for title_element in title_elements:
        href = title_element.get('href')
        loc = os.path.basename(href)
        loc = findloc(chapters, loc)
        # print(loc)
        title_name = ''.join(title_element.itertext())
        loc = os.path.join("Text", loc).replace(os.path.sep, '/')
        link = epub.Link(loc,title_name,item.id)
        same = False
        for t in toc:
            if t.href == link.href:
                same = True
                break

        if not same:
            # print(link.title,link.href,link.uid)
            yield link
    return None
def modify_img(item,chapters):

    lxml_content = item.content
    tree = etree.fromstring(lxml_content,parser=parser)
    imgs = tree.findall('.//{http://www.w3.org/1999/xhtml}img')

    namespaces = {'xlink': 'http://www.w3.org/1999/xlink', 'svg': 'http://www.w3.org/2000/svg'}
    # 查找所有 <image> 元素
    images = tree.xpath('.//svg:image', namespaces=namespaces)

    for img in imgs:
        src = img.get('src')
        loc = os.path.basename(src)
        for chapter in chapters:
            if loc in chapter:
                img.set('src',os.path.join(os.path.dirname(src),chapter).replace(os.path.sep,'/'))
                break
    for image in images:
        href = image.get('{http://www.w3.org/1999/xlink}href')
        loc = os.path.basename(href)
        for chapter in chapters:
            if loc in chapter:
                image.set('{http://www.w3.org/1999/xlink}href',os.path.join(os.path.dirname(href),chapter).replace(os.path.sep,'/'))
    return etree.tostring(tree,pretty_print=True,encoding=coding,xml_declaration=True).decode(coding)

#abandon
def modify_style(item,chapters):
    namespaces = {'xhtml': 'http://www.w3.org/1999/xhtml'}
    xhtml_content = item.content
    tree = etree.fromstring(xhtml_content,parser=parser)
    css_links = tree.xpath('//xhtml:link',namespaces=namespaces)
    html = tree.xpath('//xhtml:html',namespaces=namespaces)[0]

    for css_link in css_links:
        href = css_link.get('href')
        loc = os.path.basename(href)
        for chapter in chapters:
            if loc in chapter:
                css_link.set('href',os.path.join(os.path.dirname(href),chapter).replace(os.path.sep,'/'))
                html.append(css_link)
                break
    print(etree.tostring(html, pretty_print=True, encoding=coding, xml_declaration=True).decode(coding))
    return etree.tostring(tree,pretty_print=True,encoding=coding,xml_declaration=True).decode(coding)

def files_conbine():
    if not files:
        # messagebox.showerror("错误","你还没有选择EPUB文件")
        return
    merged_epub = epub.EpubBook()
    first_book = epub.read_epub(files[0])
    merged_epub.set_identifier(first_book.get_metadata('DC','identifier')[0][0])
    merged_epub.set_title(first_book.get_metadata('DC','title')[0][0])
    merged_epub.set_language(first_book.get_metadata('DC','language')[0][0])
    merged_epub.add_author("I dont know")

    dirs = [r'.*nav.xhtml',r'.*contents.xhtml',r'.*toc.xhtml',r'.*toc.ncx']
    dirs_patterns = [re.compile(pattern,re.IGNORECASE) for pattern in dirs]

    for i,epub_file in enumerate(files):
        try:
            book = epub.read_epub(epub_file)
            chapters = []
            toc = []
            spine = ['nav']
            for item in book.items:
                basename = os.path.basename(item.file_name)
                afterDelcration = basename[basename.rindex('.'):]

                # item.id = str(i)+ "_" + item.id
                item.id = str(i)+ "_" + basename
                if afterDelcration not in item.id:
                    item.id += afterDelcration

                item.file_name = os.path.join(os.path.dirname(item.file_name),
                                              str(i)+"_"+basename).replace(os.path.sep,'/')
                # print(item.id,item.file_name)
                chapters.append(item.id)
            for item in book.items:
                f = False
                #set toc
                for pattern in dirs_patterns:
                    if pattern.search(item.id):

                        f = True
                        add_contents = addtoc(item,chapters,toc)
                        if add_contents != None:
                            toc.extend(add_contents)
                if not f:
                    # relocalte img'src
                    if ".xhtml" in item.id:
                        modify_content = modify_img(item,chapters)
                        item.set_content(modify_content.encode(coding))
                    merged_epub.add_item(item)
            #set spine
            for t in toc:
                # print(t.href)
                for item in book.items:
                    if item.id in t.href:
                        spine.append(item.id)
            merged_epub.toc.extend(toc)
            merged_epub.spine.extend(spine)

        except Exception as e:
            print("error:",e)
            traceback.print_exc()

    nav = epub.EpubNav()
    nav.file_name = "Text/toc.xhtml"
    # merged_epub.add_item(epub.EpubNcx()) #EPUB2规范
    merged_epub.add_item(nav) #EPUB3规范
    output_file = os.path.join(os.path.dirname(files[0]), "out.epub").replace(os.path.sep,'/')
    output(output_file,merged_epub)

