from allauth.account.adapter import DefaultAccountAdapter

class MyAccountAdapter(DefaultAccountAdapter):

    def populate_username(self, request, user):
        """
        Esta función se llama cuando allauth crea un usuario
        pero el campo 'username' está vacío (como en nuestro caso).
        
        Simplemente copiaremos el email al campo username.
        """
        user.username = user.email