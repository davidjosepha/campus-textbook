import time
from splinter import Browser

# this should be ..models
# but I can't figure out the error
from campustextbook.models import (
    Book,
    BookToSection,
    Course,
    CourseSection,
    DBSession,
    Department,
    Base
    )

def get_book_id(title, author, isbn, bookstore_price_new, bookstore_price_used):
    book = DBSession.query(Book).filter(Book.isbn == isbn)
    if book.count() > 0:
        return book.one().id
    else:
        new_book = Book(
            title = title,
            author = author,
            isbn = isbn,
            bookstore_price_new = bookstore_price_new,
            bookstore_price_used = bookstore_price_used,
            )
        DBSession.add(new_book)
        DBSession.commit()

        return new_book.id

def get_dept_id(dept_name):
    dept = DBSession.query(Department).filter(Department.abbreviation == dept_name.upper())
    if dept.count() > 0:
        return dept.one().id
    else:
        new_dept = Department(
            abbreviation = dept_name.upper()
            )
        DBSession.add(new_dept) 
        DBSession.commit()

        return new_dept.id

def get_course_id(dept_name, course_number):
    dept_id = get_dept_id(dept_name)
    course = DBSession.query(Course).filter(Course.department_id == dept_id).filter(Course.course_number == course_number)
    if course.count() > 0:
        return course.one().id
    else:
        new_course = Course(
            department_id = dept_id,
            course_number = course_number
            )
        DBSession.add(new_course)
        DBSession.commit()

        return new_course.id

def get_section_id(dept_name, course_number, section_number, term, year):
    course_id = get_course_id(dept_name, course_number)
    section = DBSession.query(CourseSection).filter(CourseSection.course_id == course_id).filter(CourseSection.section_number == section_number).filter(CourseSection.term_offered == term.lower()).filter(CourseSection.year_offered == year) 
    if section.count() > 0:
        return section.one().id
    else:
        new_section = CourseSection(
            course_id = course_id,
            section_number = section_number,
            term_offered = term.lower(),
            year_offered = year,
            )
        DBSession.add(new_section)
        DBSession.commit()

        return new_section.id

def add_book_to_section(course_section_id, book_id, is_required):
    book_to_section = DBSession.query(BookToSection).filter(BookToSection.course_section_id == course_section_id).filter(BookToSection.book_id == book_id)
    if book_to_section.count() > 0:
        book_to_section.update({'is_required': is_required})
        DBSession.commit()
    else:
        new_book_to_section = BookToSection(
            course_section_id = course_section_id,
            book_id = book_id,
            is_required = is_required
            )
        DBSession.add(new_book_to_section)
        DBSession.commit()

def scrape():
    for i in range(1,44):
        with Browser('phantomjs') as browser:
            url = "http://carletonbookstore.com/SelectTermdept.aspx"
            browser.visit(url)
    
            # select term
            # id = ctl00_ctl00_Content_Content_courseSelect_ddlTerm
    
            term_select = browser.find_by_id('ctl00_ctl00_Content_Content_courseSelect_ddlTerm').last
    
            browser.execute_script("$('#ctl00_ctl00_Content_Content_courseSelect_ddlTerm>option:eq(1)').prop('selected', true);")
            browser.execute_script("setTimeout('__doPostBack(\\'ctl00$ctl00$Content$Content$courseSelect$ddlTerm\\',\\'\\')',0);")
    
            # give the js some time to work
            time.sleep(1)
    
            # select department
            # id = ctl00_ctl00_Content_Content_courseSelect_ddlDept
    
            dept_select = browser.find_by_id('ctl00_ctl00_Content_Content_courseSelect_ddlDept').last
    
            browser.execute_script("$('#ctl00_ctl00_Content_Content_courseSelect_ddlDept>option:eq(" + str(i) + ")').prop('selected', true);")
            browser.execute_script("setTimeout('__doPostBack(\\'ctl00$ctl00$Content$Content$courseSelect$ddlDept\\',\\'\\')',0);")
        
            time.sleep(1)
        
            for j in range(1,30):
                # select course
                # id = ctl00_ctl00_Content_Content_courseSelect_ddlCourse
        
                course_select = browser.find_by_id('ctl00_ctl00_Content_Content_courseSelect_ddlCourse').last
        
                browser.execute_script("$('#ctl00_ctl00_Content_Content_courseSelect_ddlCourse>option:eq(" + str(j) + ")').prop('selected', true);")
                browser.execute_script("setTimeout('__doPostBack(\\'ctl00$ctl00$Content$Content$courseSelect$ddlCourse\\',\\'\\')',0);")
        
                # submit button
                # id = ctl00_ctl00_Content_Content_btnAddCourseToList
        
                add_course = browser.find_by_id('ctl00_ctl00_Content_Content_btnAddCourseToList').last
                add_course.click()
                time.sleep(.5)
                
            # submit button 2
            # id = ctl00_ctl00_Content_Content_btnGetCourseMaterials
            get_courses = browser.find_by_id('ctl00_ctl00_Content_Content_btnGetCourseMaterials').last
            get_courses.click()
    
            time.sleep(1)
    
            # read HTML!!!
            # aghhhhh
    
            # after j = 9, there's a "next" button
            # to get to the next page
            # numbering then resets at 0
            # need to add this...
            j = 0
            while True:
                if j == 10:
                    # click "next page" link
                    # set j to 0

                    # but, for now:
                    break

                try:
                    course_info = browser.find_by_xpath('//div[@id="wrapper"]/div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_courseInfo"]/div[@class="term_bar"]/h2/span').value
                except:
                    break
    
                material_info = browser.find_by_xpath('//div[@id="wrapper"]/div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_courseInfo"]/div[@class="material_info"]')
                pricing_info = browser.find_by_xpath('//div[@id="wrapper"]/div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_courseInfo"]/div[@class="pricing_wrapper"]')
    
                for k in range(len(material_info)):
                    # need to replace the 0 + str(k) with k formatted as a 2 digit int
                    title_path = '//div[@id="wrapper"]/div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_courseInfo"]/div[@class="material_info"]/h3/span'
                    # this might not be right
                    required_path = '//div[@id="wrapper"]/div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_courseInfo"]/div[@class="material_info"]/div[@class="material_label"]/span'
                    author_path = '//div[@id="wrapper"]/div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_courseInfo"]/div[@class="material_info"]//tr[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_rptItems_ctl' + str(k).zfill(2) + '_rowAuthor"]/td[@class="right_side"]'
                    isbn_path = '//div[@id="wrapper"]/div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_courseInfo"]/div[@class="material_info"]//tr[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_rptItems_ctl' + str(k).zfill(2) + '_pnlItemTxtDisplayISBN"]/td[@class="right_side"]'
    
                    used_path = '//div[@id="wrapper"]/div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_courseInfo"]/div[@class="pricing_wrapper"]//div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_rptItems_ctl' + str(k).zfill(2) + '_div_used"]//p[@class="price"]/span'
                    new_path = '//div[@id="wrapper"]/div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_courseInfo"]/div[@class="pricing_wrapper"]//div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_rptItems_ctl' + str(k).zfill(2) + '_div_new"]//p[@class="price"]/span'
    
                    title = browser.find_by_xpath(title_path)[k].value
                    required = browser.find_by_xpath(required_path)[k].value
                    if required.strip().lower() == 'required':
                        is_required = True
                    else:
                        is_required = False

                    author = browser.find_by_xpath(author_path).value
                    isbn = browser.find_by_xpath(isbn_path).value
    
                    # not sure if try/except is acceptable
                    # here but they sometimes put a string
                    # there I've only seen it be 'TBD' but
                    # I don't want to assume it always is
                    used = browser.find_by_xpath(used_path)
                    #if hasattr(used, 'value'):
                    try:
                        bookstore_price_used = float(used.value.strip('$'))
                    except:
                        bookstore_price_used = 0
    
                    new = browser.find_by_xpath(new_path)
                    #if hasattr(new, 'value'):
                    try:
                        bookstore_price_new = float(new.value.strip('$'))
                    except:
                        bookstore_price_new = 0
    
                    course_meta = course_info.split(':')
                    term = course_meta[1].strip().split(' ')[0].lower()
                    year = int(course_meta[1].strip().split(' ')[1])
                    dept_name = course_meta[2].strip().split(' ')[:-1][0]
                    course_number = int(course_meta[2].strip().split(' ')[:-1][1])
                    section_number = int(course_meta[3].strip().split(' ')[:-1][0])
                    professor = " ".join(course_meta[4].strip().split(' ')[:-1])
                    book_id = get_book_id(title, author, isbn, bookstore_price_new, bookstore_price_used)
                    section_id = get_section_id(dept_name, course_number, section_number, term, year)
                    add_book_to_section(section_id, book_id, is_required)

                j += 1
