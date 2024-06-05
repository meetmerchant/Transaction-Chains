'''
server 1: book, member
server 2: book, member
server 3: borrow, reservation
server 4: fine, staff
'''

class TransactionChopper:
    def __init__(self):
        self.chops = {
            'T1': [('read from staff', 4, [])],
            'T2': [('read from book', 1, [1]), ('read from member', 100, [1]), ('insert into borrow', 3, [1, 100, 1, '05/05/24', '05/25/24', '05/20/24'])],
            'T3': [('read from book', 2, [2]), ('read from member', 2, [200]), ('insert into reservation', 3, [1, 200, 2, '06/04/24', 'Reserved'])],
            'T4': [('insert into member', 1, [300, 'Bob', 'bob@gmail.com', '67890', 'Newport, CA', '06/04/24'])],
            'T5': [('insert into book', 2, [3, 'Algorithms', 'Goodrich', 5, 4])],
            'T6': [('insert into staff', 4, [1, 'Alice', 'alice@gmail.com', '12345', 'Irvine, CA', 'Manager', '04/06/24'])],
            'T7': [('update book', 1, [4, 10]), ('update borrow', 3, [2, '06/05/24']), ('insert into fine', 4, [1, 3, 100, False, '06/05/24'])]
        }

    def get_chops(self, transaction):
        return [(transaction, self.chops.get(transaction, []))]

# Example usage
chopper = TransactionChopper()
chopper.chop_transaction('T7')
print("Chops for T7:", chopper.get_chops('T7'))
print("Chops for T8:", chopper.get_chops('T8'))
