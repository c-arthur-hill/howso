def get_current_path(request):
    return {
       'current_path': request.get_full_path()
     }

def request_is_ajax(request):
    return {
       'ajax': request.is_ajax()
    }
