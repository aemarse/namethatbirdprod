import create_lesson as cl

filepath = "/Users/aemarse/Documents/devel/NameThatBird/bird_lists/central_park.csv"

lesson = cl.Lesson()
x = lesson.from_csv(filepath)

print x
