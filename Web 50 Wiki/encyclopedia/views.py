
from django import forms
from django.shortcuts import render
from django.shortcuts import redirect
from markdown2 import markdown
from random import choice
from . import util


class SearchForm(forms.Form):
    q = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia'}))


class NewPageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    page_content = forms.CharField(label="",
                                   widget=forms.Textarea(attrs={'style': 'height: 60vh; width:100%, resize: none',
                                                                'placeholder': 'Content'}))


form1 = SearchForm
form2 = NewPageForm


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": form1()
    })


def render_entry(request, title):
    entry = util.get_entry(title)
    if entry:
        return render(request, "encyclopedia/title.html", {
            "title": title,
            "entry": markdown(entry),
            "form": form1()})
    else:
        return render(request, "encyclopedia/error.html")


def search(request):
    query = request.GET.get("q").lower()
    list_entries = util.list_entries()
    list_entries_lower = [x.lower() for x in util.list_entries()]
    entry = True if (query in list_entries_lower) else False

    if entry:
        title = query
        return redirect(f"entry", title=title)
    else:
        filtered: list = list(filter(lambda entry_title: query in entry_title.lower(), list_entries))
        if bool(len(filtered)):
            return render(request, "encyclopedia/search.html", {"substring_entries": filtered, "form": form1(),
                                                                "query": query})

    return render(request, "encyclopedia/search.html", {"query": query, "form": form1() })


def create_page(request):
    template = "encyclopedia/create_page.html"
    if request.method == "POST":
        form = NewPageForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            page_content = form.cleaned_data["page_content"]
            form.title = forms.CharField(label="", initial=title)
            form.page_content = forms.CharField(label="", initial=page_content,
                                   widget=forms.Textarea(attrs={'style': 'height: 60vh; width:100%, resize: none'}))
            list_entries = [x.lower() for x in util.list_entries()]

            if title.lower() in list_entries:
                return render(request, template, {"form": form1(), "page_create_form": form, "Page_exists": True,
                                                  "title": title, "page_content": page_content})
            else:
                util.save_entry(title, page_content)
                return redirect(f"entry", title=title)

    return render(request, template, {"form": form1(), "page_create_form": form2()})


def edit_page(request):
    template = "encyclopedia/edit_page.html"
    title_page = "encyclopedia/title.html"
    if request.method == "GET":
        title = request.GET.get("title")
        content = util.get_entry(title)
        return render(request, template, {"form": form1(), "title": title, "page_content": content})

    if request.method == "POST":
        form = form2(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["page_content"]
            util.save_entry(title, content)
            return redirect(f"entry", title=title)


def random_page(request):
    random_title = choice(util.list_entries())
    return redirect(f"entry", title=random_title)
