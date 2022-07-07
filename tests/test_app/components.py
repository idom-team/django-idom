import idom

import django_idom

from . import views


@idom.component
def hello_world():
    return idom.html.h1({"id": "hello-world"}, "Hello World!")


@idom.component
def button():
    count, set_count = idom.hooks.use_state(0)
    return idom.html.div(
        idom.html.button(
            {"id": "counter-inc", "onClick": lambda event: set_count(count + 1)},
            "Click me!",
        ),
        idom.html.p(
            {"id": "counter-num", "data-count": count},
            f"Current count is: {count}",
        ),
    )


@idom.component
def parameterized_component(x, y):
    total = x + y
    return idom.html.h1({"id": "parametrized-component", "data-value": total}, total)


victory = idom.web.module_from_template("react", "victory-bar", fallback="...")
VictoryBar = idom.web.export(victory, "VictoryBar")


@idom.component
def simple_bar_chart():
    return VictoryBar()


@idom.component
def use_websocket():
    ws = django_idom.hooks.use_websocket()
    ws.scope = "..."
    success = bool(ws.scope and ws.close and ws.disconnect and ws.view_id)
    return idom.html.div(
        {"id": "use-websocket", "data-success": success},
        idom.html.hr(),
        f"use_websocket: {ws}",
        idom.html.hr(),
    )


@idom.component
def use_scope():
    scope = django_idom.hooks.use_scope()
    success = len(scope) >= 10 and scope["type"] == "websocket"
    return idom.html.div(
        {"id": "use-scope", "data-success": success},
        f"use_scope: {scope}",
        idom.html.hr(),
    )


@idom.component
def use_location():
    location = django_idom.hooks.use_location()
    success = bool(location)
    return idom.html.div(
        {"id": "use-location", "data-success": success},
        f"use_location: {location}",
        idom.html.hr(),
    )


@idom.component
def django_css():
    return idom.html.div(
        {"id": "django-css"},
        django_idom.components.django_css("django-css-test.css"),
        idom.html.div({"style": {"display": "inline"}}, "django_css: "),
        idom.html.button("This text should be blue."),
        idom.html.hr(),
    )


@idom.component
def django_js():
    success = False
    return idom.html._(
        idom.html.div(
            {"id": "django-js", "data-success": success},
            f"django_js: {success}",
            django_idom.components.django_js("django-js-test.js"),
        ),
        idom.html.hr(),
    )


@idom.component
def view_to_component():
    return django_idom.utils.view_to_component(views.view_to_component)


@idom.component
def view_to_component_async():
    return django_idom.utils.view_to_component(views.view_to_component_async)


@idom.component
def view_to_component_class():
    return django_idom.utils.view_to_component(views.ViewToComponentClass)


@idom.component
def view_to_component_compatibility():
    return idom.html.div(
        {"id": "view_to_component_compatibility"},
        django_idom.utils.view_to_component(
            views.view_to_component_compatibility, compatibility=True
        ),
        idom.html.hr(),
    )


@idom.component
def view_to_component_middleware():
    def str_replace_middleware(view):
        def middleware(request, *args, **kwargs):
            render = view(request, *args, **kwargs)
            render.content = render.content.decode("utf-8").replace("Fail", "Success")
            return render

        return middleware

    return django_idom.utils.view_to_component(
        views.view_to_component_middleware, middleware=[str_replace_middleware]
    )


@idom.component
def view_to_component_script():
    return django_idom.utils.view_to_component(views.view_to_component_script)
