import os
from datetime import datetime 
from datetime import date
from src.receiptScan import Scan
import re
from src.view import View


def getCategories():
  with open('src/Data/spendingCategories.txt', 'r') as file:
    data = file.read()
    categories = data.splitlines()
    return categories


class Expenses:

  def __init__(self):
    self.categories = getCategories()


  def printCategories(self):
    print('-'*30)
    print('CATEGORIES:')
    for i,x in enumerate(self.categories):
      print(f'{i+1} {x}')
    print()


  def addCategory(self):
    print('-'*30)
    newCategory = str(input("Enter the new category: "))
    self.categories.append(newCategory)
    with open('src/Data/spendingCategories.txt', 'a') as file:
      file.write(newCategory+'\n')
    with open(f'src/Data/{newCategory}.txt','w') as file:
      file.write('0\n')
    print(f"Category {newCategory} was added:")


  def removeCategoryFromAll(self, category:str):
    lines = []
    removedExpenses = []
    newAmount = 0.0
    with open('src/Data/allExpenses.txt', 'r') as file:
      lines = file.readlines()
      newAmount = float(lines[0])
      for i in range(1,len(lines)):
        data = re.split('\||\n', lines[i])
        if data[1] == category:
          removedExpenses.append(lines[i])
          newAmount = newAmount - float(data[2])
      for expense in removedExpenses:
        lines.remove(expense)
    lines[0] = str(newAmount) + '\n'
    with open('src/Data/allExpenses.txt', 'w') as file:
      for line in lines:
        file.write(line)



  def removeCategory(self): 
    print("Select a category to be removed")
    index = self.getValidCategory()
    category = self.categories[index-1]
    if self.getValidYN(f"Confirm removal of the {category} category? (y/n): ") == 'y':
      os.remove(f"src/Data/{category}.txt")
      print(f"CATEGORY REMOVED: {category}")
      self.categories.remove(category)
      with open('src/Data/spendingCategories.txt', 'w') as file:
        for c in self.categories:
          file.write(c + '\n')
      self.removeCategoryFromAll(category)
    else:
      print("Canceling Removal")


  def scanReceipt(self):
    scanner = Scan()
    scanner.captureImage()
    scanner.processImage()
    return scanner.findTotal()


  def checkCategoryNum(self, num): 
    return num >= 0 and num <= len(self.categories)


  def getValidYN(self, response:str):
    scan = ""
    while scan != "y" and scan != "n":
      scan = str(input(response))
    return scan


  def getExpenseInfo(self, data:dict):
    if len(data) == 1:
      validAmount = False
      total = 0.00
      while not validAmount:
        try: 
          total = float(input("Enter amount: $"))
          if total > 0:
            validAmount = True
        except ValueError:
          print("Entry is invalid")
      data['total'] = total
    
    validDate = False
    while not validDate:
      try:
        expenseDate = input('Enter date: "YYYY-MM-DD" or "Today": ')
        if expenseDate.isalpha():
          expenseDate = expenseDate.lower()
          if expenseDate == 'today':
            today = date.today()
            expenseDate = today.strftime('%Y-%m-%d')
            validDate = True
        else:
          datetime.strptime(expenseDate, '%Y-%m-%d')
          validDate = True
      except ValueError:
        print("Incorrect date format, should be YYYY-MM-DD")
    data['date'] = expenseDate
    validDetails = False
    details = ""
    while not validDetails:
      details = input("Enter any details: ")
      if details.find('|') == -1:
        validDetails = True
      else:
        print("Invalid Character '|'")
    data['details'] = details
    return data


  def addtoAll(self, data:dict):
    with open('src/Data/allExpenses.txt', 'r+') as file:
      lines = file.readlines()
      entries = []
      totalAmt = 0.00
      for i in range(1,len(lines)):
        expenseInfo = re.split('\||\n', lines[i])
        entries.append({'category' : expenseInfo[1],
                        'total' : expenseInfo[2],
                        'date' : expenseInfo[0],
                        'details' : expenseInfo[3]})
        totalAmt = totalAmt + float(expenseInfo[2])
      entries.append(data)
      totalAmt = totalAmt + float(data['total'])
      entries.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
      file.truncate(0)
      file.seek(0)
      file.write(f'{totalAmt}\n')
      for entry in entries:
        file.write(f"{entry['date']}|{entry['category']}|{entry['total']}|{entry['details']}\n")


  def addtoCategory(self, data:dict):
    with open(f"src/Data/{data['category']}.txt".format(), 'r+') as file:
      lines = file.readlines()
      entries = []
      totalAmt = 0.00
      for i in range(1,len(lines)):
        expenseInfo = re.split('\||\n', lines[i]) 
        entries.append({'total' : expenseInfo[1],
                        'date' : expenseInfo[0],
                        'details' : expenseInfo[2]})
        totalAmt = totalAmt + float(expenseInfo[1])
      entries.append({'total' : data['total'],
                      'date' : data['date'],
                      'details' : data['details']})
      totalAmt = totalAmt + float(data['total'])
      entries.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
      file.truncate(0)
      file.seek(0)
      file.write(f'{totalAmt}\n')
      for entry in entries:
        file.write(f"{entry['date']}|{entry['total']}|{entry['details']}\n")


  def recordExpense(self, data:dict):
    self.addtoAll(data)
    self.addtoCategory(data)


  def printAddedExpenseSummary(self, data:dict):
    print('-'*30)
    print("SUMMARY OF ADDED EXPENSE")
    print(f"Date: {data['date']}")
    print(f"Category: {data['category']}")
    print(f"Total: ${data['total']}")
    print(f"Details: {data['details']}")


  def getValidCategory(self):
    self.printCategories()
    validResponse = False
    while not validResponse:
      try:
        index = int(input("Enter the category number: "))
        validResponse = self.checkCategoryNum(index-1)
      except ValueError:
        print("Enter the number corresponding to the categories stated above")
    return index


  def addExpense(self):
    print('-'*30)
    print("ADDING EXPENSE")
    index = self.getValidCategory()

    category = self.categories[index-1]
    scan = self.getValidYN("Would you like to scan a receipt? (y/n): ")

    total = 0
    correctTotal = False
    expenseData = dict({'category' : category})
    if (scan == 'y'):
      while True:
        total = self.scanReceipt()
        if total == -1.0:
          print("Cannot read image")
        elif (self.getValidYN(f"Is this the correct total? ${total} (y/n): ") == 'y'):
          correctTotal = True
          break
        if (self.getValidYN("Would you like to scan again? (y/n): ") == 'n'):
          break

      if correctTotal:
        expenseData['total'] = total

    expenseData = self.getExpenseInfo(expenseData)
    self.recordExpense(expenseData)
    self.printAddedExpenseSummary(expenseData)


  def emptyCategory(self, category:str):
    with open(f'src/Data/{category}.txt', 'r') as file:
      lines = file.readlines()
      amount = lines[0].split()
      amount = float(amount[0])
      if amount == 0:
        return True
    return False


  def removeFromFile(self, expense:str, category:str):
    data = re.split('\||\n', expense)
    removedCost = float(data[1])
    print(removedCost)
    with open(f'src/Data/{category}.txt', 'r+') as file:
      lines = file.readlines()
      newTotal = float(lines[0]) - removedCost
      lines[0] = str(newTotal) + '\n'
      lines.remove(expense)
      file.truncate(0)
      file.seek(0)
      for line in lines:
        file.write(line)
    with open(f'src/Data/allExpenses.txt', 'r+') as file:
      lines = file.readlines()
      newTotal = float(lines[0]) - removedCost
      lines[0] = str(newTotal) + '\n'
      expense = expense[:11] + category + '|' + expense[11:]
      lines.remove(expense)
      file.truncate(0)
      file.seek(0)
      for line in lines:
        file.write(line)


  def removeExpense(self): 
    print('-'*30)
    print('REMOVING EXPENSE\n')
    print("From which category is the expense from?")
    categoryIndex = self.getValidCategory()
    category = self.categories[categoryIndex-1]
    if (self.emptyCategory(category) == True):
      print("\nEmpty Category")
      print("Canceling Removal")
      return
    catExpenses = View()
    catExpenses.viewCategoryExpenses(category)
    print('-'*30)
    with open(f'src/Data/{category}.txt', 'r') as file:
      lines = file.readlines()
      indexes = len(lines)-1 
      isValidIndex = False
      expenseIndex = 0 
      while not isValidIndex:
        try:
          expenseIndex = int(input("Enter the index of the expense that will be removed: "))
          if expenseIndex >= 1 and expenseIndex <= indexes:
            isValidIndex = True
          else:
            print("Enter valid index")
        except ValueError:
          print("Enter valid index")
      data = re.split('\||\n', lines[expenseIndex])
      if self.getValidYN(f"\nREMOVING EXPENSE\nDATE: {data[0]}\nAMOUNT: ${data[1]}\nDETAILS: {data[2]}\nCONFIRM REMOVAL? (y/n): ") == 'y':
        self.removeFromFile(lines[expenseIndex], category)
        print('-'*30)
        print("REMOVAL SUMMARY:")
        print(f"DATE: {data[0]}\nCATEGORY: {category}\nAMOUNT: ${data[1]}\nDETAILS: {data[2]}\n")
      else:
        print("Canceling removal")