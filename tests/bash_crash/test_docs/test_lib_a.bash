# test lib a

line a.1
line a.2

#% ignore {
line a.ignore.1
line a.ignore.2
#% }

#% include "./test_lib_b.bash" {
line stub for b
#% }

line a.3
