from django.template import Context, Template
from django.test import SimpleTestCase, override_settings

from django_vite_tags.templatetags.vite_tags import DjangoViteManifestError


class TestDjangoViteTags(SimpleTestCase):
    def test_adds_expected_tags_for_foo(self):
        template = Template("{% load vite_tags %}{% vite 'views/foo.js' %}")
        result = template.render(Context({}))
        self.assertHTMLEqual(
            result,
            """
            <link rel="stylesheet" href="assets/foo-5UjPuW-k.css" />
            <link rel="stylesheet" href="assets/shared-ChJ_j-JJ.css" />
            <script type="module" src="assets/foo-BRBmoGS9.js"></script>
            <link rel="modulepreload" href="assets/shared-B7PI925R.js" />
            """,
        )

    def test_adds_expected_tags_for_bar(self):
        template = Template("{% load vite_tags %}{% vite 'views/bar.js' %}")
        result = template.render(Context({}))
        self.assertHTMLEqual(
            result,
            """
            <link rel="stylesheet" href="assets/shared-ChJ_j-JJ.css" />
            <script type="module" src="assets/bar-gkvgaI9m.js"></script>
            <link rel="modulepreload" href="assets/shared-B7PI925R.js" />
            """,
        )

    @override_settings(DJANGO_VITE_SERVER_URL="http://localhost:5173")
    def test_adds_expected_tags_when_vite_server_set(self):
        template = Template("{% load vite_tags %}{% vite 'main.js' %}")
        result = template.render(Context({}))
        self.assertHTMLEqual(
            result,
            """
            <script type="module" src="http://localhost:5173/@vite/client"></script>
            <script type="module" src="http://localhost:5173/main.js"></script>
            """,
        )

    def test_raises_exception_for_unexpected_entrypoint(self):
        template = Template("{% load vite_tags %}{% vite 'main.js' %}")
        with self.assertRaises(DjangoViteManifestError):
            template.render(Context({}))
