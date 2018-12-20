import pathlib
import shutil
import string

from models import *


def format_filename(s: str) -> str:
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    # filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
    return filename


def create_library(librarydir: pathlib.Path, browsedir: pathlib.Path):
    shutil.rmtree(browsedir)
    browsedir.mkdir()
    print("title")
    title_dir = browsedir / "title"
    title_dir.mkdir(exist_ok=True)
    for paper in Paper.select():
        sourcefile = librarydir / "{}.pdf".format(paper.id)
        targetfile = title_dir / "{}.pdf".format(format_filename(paper.title))
        targetfile.symlink_to(sourcefile)

    print("author")
    author_dir = browsedir / "authors"
    author_dir.mkdir(exist_ok=True)
    for author in Author.select():
        author_subdir = author_dir / format_filename(author.name)
        author_subdir.mkdir()
        for paper in Paper.select().join(PaperAuthors).where(PaperAuthors.author == author):
            sourcefile = librarydir / "{}.pdf".format(paper.id)
            targetfile = author_subdir / "{}.pdf".format(format_filename(paper.title))
            targetfile.symlink_to(sourcefile)

    print("keywords")
    keywords_dir = browsedir / "keywords"
    keywords_dir.mkdir(exist_ok=True)
    for keyword in Keyword.select():
        keyword_subdir = keywords_dir / format_filename(keyword.keyword)
        keyword_subdir.mkdir()
        for paper in Paper.select().join(PaperKeywords).where(PaperKeywords.keyword == keyword):
            sourcefile = librarydir / "{}.pdf".format(paper.id)
            targetfile = keyword_subdir / "{}.pdf".format(format_filename(paper.title))
            targetfile.symlink_to(sourcefile)
