from pyramid.view import view_config
import pyramid.httpexceptions as exc


@view_config(route_name='api_test', request_method='GET')
def suivi_mandats_view(request):
    """
    Return httpok
    """
    # Check if the api is working successfully
    return exc.HTTPOk ("Yeah, your api is working!")

