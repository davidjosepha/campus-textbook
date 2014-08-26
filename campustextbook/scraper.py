import time
from splinter import Browser

# this should be ..models
# but I can't figure out the error, so
# probably need an __init__.py in this directory?
from campustextbook.models import (
    Book,
    DBSession,
    Base
    )

def scrape():
    course_infos = []
    for i in range(1,3):
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
    
            # go to wrapper
            #for j in range(1):
            j = -1
            while True:
                j += 1
                try:
                    course_info = browser.find_by_xpath('//div[@id="wrapper"]/div[@id="ctl00_ctl00_Content_Content_rptCourses_ctrl' + str(j) + '_courseInfo"]/div[@class="term_bar"]/h2/span').value
    
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
                        author = browser.find_by_xpath(author_path).value
                        isbn = browser.find_by_xpath(isbn_path).value
    
                        
                        used = browser.find_by_xpath(used_path)
                        if hasattr(used, 'value'):
                            used_price = used.value
                        else:
                            used_price = '$0'
    
                        new = browser.find_by_xpath(new_path)
                        if hasattr(new, 'value'):
                            new_price = new.value
                        else:
                            new_price = '$0'
    
                        course_meta = course_info.split(':')
                        term = " ".join(course_meta[1].strip().split(' ')[:-1])
                        dept = course_meta[2].strip().split(' ')[:-1][0]
                        number = course_meta[2].strip().split(' ')[:-1][1]
                        section = course_meta[3].strip().split(' ')[:-1][0]
                        instructor = " ".join(course_meta[4].strip().split(' ')[:-1])
                        course_infos.append([term, dept, number, section, instructor, title, required, author, isbn, used_price, new_price])
                        #print(term + " - " + dept + "-" + number + "-" + section + " - " + instructor + " - " + title + " - " + required + " - " + author + " - " + isbn + " - " + used_price + " - " + new_price)
                        book = Book(
                            title = title,
                            author = author,
                            isbn = isbn,
                            )

                        DBSession.add(book)

                except:
                    break
    
    
    return course_infos
