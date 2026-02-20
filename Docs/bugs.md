# Testing Bugs
original Format = DT-number | type : message
number and message is known by developer and types are 
allowed-types = [ "FEAT", "FIX", "INIT", "DOCS", "REFACTOR", "TEST", "CHORE",]


# Test 1
 // testing if Changes in Dt component works

 input - git commit -m "DB-14 | DOCS : Testing Bug No-1"

 output - [main 6501570] DB-14 | DOCS : Testing Bug No-1
 1 file changed, 1 insertion(+), 1 deletion(-)

 result - Enforcer Bypassed


 # Test 2
 // testing if numbers are invalid still works or not 

 input -git commit -m "DB-e | DOCS : Testing Bug No-2" 

 output - Invalid commit format! Expected: TICKET | TYPE : description
Got: DB-e | DOCS : Testing Bug No-2

Result - Enforcer Working properly.

 # Test 3
 // testing if DT is replaced by a number then enforcer stops it or not.
  
input -git commit -m "11-14 | DOCS : Testing Bug No-3"

output -Invalid commit format! Expected: TICKET | TYPE : description
Got: 11-14 | DOCS : Testing Bug No-3

Result - Enforcer Working properly.

 # Test 4
 // testing if types can be out of the fields which are pre defined 

 input -git commit -m "DB-14 | XYZ : Testing Bug No-4"

 Output - Unknown type: XYZ (allowed: FEAT, FIX, INIT, DOCS, REFACTOR, TEST, CHORE)

Result - Enforcer Working properly.

  # Test 5
  // testing if db can be written anything in alphabets 

  input -git commit -m "SRV-14 | DOCS : Testing Bug No-5"

  output -[main 0378076] SRV-14 | DOCS : Testing Bug No-5
 1 file changed, 16 insertions(+), 18 deletions(-)

 result - Enforcer Bypassed

 # Test 6
// testing if overall structures matter or not 

input -git commit -m "11-e|123:Testing Bug No-6"

output -Invalid commit format! Expected: TICKET | TYPE : description
Got: this is a bad commit

Result - Enforcer Working properly.

# Test 7
// testing if number could be any invalid number

input -git commit -m "SRV-144444 | DOCS : Testing Bug No-5"  

output - [main b21605a] SRV-144444 | DOCS : Testing Bug No-5
 1 file changed, 9 insertions(+), 4 deletions(-)

 result - Enforcer Bypassed