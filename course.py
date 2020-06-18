from discord import Embed

class Course:
    def __init__(self, dept_code, course_number, course_title, num_units, course_desc, requisite, grading, repeatability, restriction, ge_req, similar, overlaps):
        self.dept_code = dept_code
        self.course_number = course_number
        self.course_title = course_title
        self.num_units = num_units
        self.course_desc = course_desc

        self.requisite = requisite
        self.grading = grading
        self.repeatability = repeatability
        self.restriction = restriction
        self.ge_req = ge_req
        self.similar = similar
        self.overlaps = overlaps


    @classmethod
    def from_dict(cls, dept_code, a_dict):
        return cls(dept_code, a_dict['course_number'], a_dict['course_title'], a_dict['num_units'], 
        a_dict['course_desc'], a_dict['requisite'], a_dict['grading'], a_dict['repeatability'], a_dict['restriction'], a_dict['ge_req'], a_dict['similar'], a_dict['overlaps'])

    def to_embed(self):
        embed = Embed(title=f'{self.course_title}', description=f'{self.dept_code} {self.course_number} - *{self.num_units}*', color=0x879BAF)
        if self.course_desc != '':
            embed.add_field(name="Course Description", value=self.course_desc, inline=False)
        if self.requisite != '':
            embed.add_field(name="Course Requisites", value=self.requisite, inline=False)
       
        if self.restriction != '':
            embed.add_field(name="Course Restrictions", value=self.restriction, inline=False)
       
        if self.similar != '':
            embed.add_field(name="Similar Courses", value=self.similar, inline=False)
        if self.overlaps != '':
            embed.add_field(name="Course Overlaps", value=self.overlaps, inline=False)
        if self.grading != '':
            embed.add_field(name="Grading Options", value=self.grading, inline=False)
        if self.repeatability != '':
            embed.add_field(name="Course Repeatability", value=self.repeatability, inline=False)
        if self.ge_req != '':
            embed.add_field(name="Satisfies GE Requirement", value=self.ge_req, inline=False)
        return embed
    def __str__(self):
        return \
f'''
{self.dept_code} {self.course_number}
{self.course_title} - {self.num_units}
{self.course_desc}

{self.requisite}
{self.grading}
{self.repeatability}
{self.restriction}
{self.ge_req}
{self.similar}
{self.overlaps}
'''