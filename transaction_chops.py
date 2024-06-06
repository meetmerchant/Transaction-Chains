'''
server 1: book, member
server 2: book, member
server 3: borrow, reservation
server 4: fine, staff
'''

class TransactionChopper:
    def __init__(self):
        self.chops = {
            'T1': [('SELECT * FROM staff', 4, [])],
            'T2': [('SELECT * FROM book WHERE id = ?', 1, [1]), ('SELECT * FROM member WHERE id = ?', 1, [100]), ('INSERT INTO borrow VALUES (?, ?, ?, ?, ?, ?)', 3, [1, 100, 1, '05/05/24', '05/25/24', '05/20/24'])],
            'T3': [('SELECT * FROM book WHERE id = ?', 2, [2]), ('SELECT * FROM member WHERE id = ?', 2, [200]), ('INSERT INTO reservation VALUES (?, ?, ?, ?, ?)', 3, [1, 200, 2, '06/04/24', 'Reserved'])],
            'T4': [('INSERT INTO member VALUES (?, ?, ?, ?, ?, ?)', 1, [300, 'Bob', 'bob@gmail.com', '67890', 'Newport, CA', '06/04/24'])],
            'T5': [('INSERT INTO book VALUES (?, ?, ?, ?, ?)', 2, [3, 'Algorithms', 'Goodrich', 5, 4])],
            'T6': [('INSERT INTO staff VALUES (?, ?, ?, ?, ?, ?, ?)', 4, [1, 'Alice', 'alice@gmail.com', '12345', 'Irvine, CA', 'Manager', '04/06/24'])],
            'T7': [('UPDATE book SET quantity = ? WHERE id = ?', 1, [10, 4]), ('UPDATE borrow SET return_date = ? WHERE id = ?', 3, ['06/05/24', 2]), ('INSERT INTO fine VALUES (?, ?, ?, ?, ?)', 4, [1, 3, 100, False, '06/05/24'])]
        }

    def get_chops(self, transaction):
        return self.chops.get(transaction, [])

# Example usage
'''
chopper = TransactionChopper()
print("Chops for T7:", chopper.get_chops('T7'))
print("Chops for T8:", chopper.get_chops('T8'))
'''
