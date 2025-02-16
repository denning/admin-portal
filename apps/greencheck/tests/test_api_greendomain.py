import csv
import io
import logging
from typing import List


import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from ..legacy_workers import LegacySiteCheckLogger
from ..models import GreencheckIp, GreenDomain

from ...accounts import models as ac_models

from ..viewsets import GreenDomainViewset
from . import greencheck_sitecheck, setup_domains

User = get_user_model()

pytestmark = pytest.mark.django_db

logger = logging.getLogger(__name__)

rf = APIRequestFactory()


def parse_csv_from_response(response):
    """
    Convenience function for working with CSV responses.
    Parses the CSV rows and returns a list of dicts, using the
    keys as columns
    """
    file_from_string = io.StringIO(response.content.decode("utf-8"))
    parsed_rows = []
    reader = csv.DictReader(file_from_string)

    for row in reader:
        logger.debug(row)
        parsed_rows.append(row)

    return parsed_rows


class TestGreenDomainViewset:
    """"""

    def test_check_single_url(
        self,
        hosting_provider: ac_models.Hostingprovider,
        sample_hoster_user: User,
        green_ip: GreencheckIp,
    ):
        """
        Check single URL, hitting.
        """

        hosting_provider.save()
        sample_hoster_user.hostingprovider = hosting_provider
        sample_hoster_user.save()
        sitecheck_logger = LegacySiteCheckLogger()

        domain = "google.com"

        sitecheck = greencheck_sitecheck(domain, hosting_provider, green_ip)

        sitecheck_logger.update_green_domain_caches(sitecheck, hosting_provider)

        rf = APIRequestFactory()
        url_path = reverse("green-domain-detail", kwargs={"url": domain})
        logger.info(f"url_path: {url_path}")

        request = rf.get(url_path)

        view = GreenDomainViewset.as_view({"get": "retrieve"})

        response = view(request, url=domain)

        assert response.status_code == 200
        assert response.data["green"] is True

    def test_check_multple_urls_get(
        self,
        hosting_provider: ac_models.Hostingprovider,
        sample_hoster_user: User,
        green_ip: GreencheckIp,
    ):
        """
        Check multiple URLs, sent as a batch request
        """

        hosting_provider.save()
        sample_hoster_user.hostingprovider = hosting_provider
        sample_hoster_user.save()
        sitecheck_logger = LegacySiteCheckLogger()

        domains = ["google.com", "anothergreendomain.com"]
        COMMA_SEPARATOR = ","
        domain_string = COMMA_SEPARATOR.join(domains)

        for domain in domains:
            sitecheck = greencheck_sitecheck(domain, hosting_provider, green_ip)
            sitecheck_logger.update_green_domain_caches(sitecheck, hosting_provider)

        rf = APIRequestFactory()
        url_path = reverse("green-domain-list")
        request = rf.get(url_path, {"urls": domain_string})

        view = GreenDomainViewset.as_view({"get": "list"})

        response = view(request)
        assert response.status_code == 200
        logger.debug("response.data")
        logger.debug(response.data)
        assert len(response.data) == 2
        return_domains = [datum["url"] for datum in response.data]
        for domain in domains:
            assert domain in return_domains

    def test_check_multple_urls_post(
        self,
        hosting_provider: ac_models.Hostingprovider,
        sample_hoster_user: User,
        green_ip: GreencheckIp,
    ):
        """
        Check multiple URLs, sent as a batch request
        """

        hosting_provider.save()
        sample_hoster_user.hostingprovider = hosting_provider
        sample_hoster_user.save()
        sitecheck_logger = LegacySiteCheckLogger()

        domains = ["google.com", "anothergreendomain.com"]

        for domain in domains:
            sitecheck = greencheck_sitecheck(domain, hosting_provider, green_ip)
            sitecheck_logger.update_green_domain_caches(sitecheck, hosting_provider)

        rf = APIRequestFactory()
        url_path = reverse("green-domain-list")
        request = rf.post(url_path, {"urls": domains})

        view = GreenDomainViewset.as_view({"post": "list"})

        response = view(request)
        assert response.status_code == 200
        logger.debug("response.data")
        logger.debug(response.data)
        assert len(response.data) == 2
        return_domains = [datum["url"] for datum in response.data]
        for domain in domains:
            assert domain in return_domains

    def test_check_single_url_new_domain(
        self,
        hosting_provider_with_sample_user: ac_models.Hostingprovider,
        green_ip: GreencheckIp,
    ):
        """
        Exercise the checking code, when we don't have our domain cached already.
        We don't persist the newly discovered green domain here to the database, but
        in prod, we'd delegate it to a worker.
        """

        setup_domains(["google.com"], hosting_provider_with_sample_user, green_ip)

        # this serves as a url that corresponds to the green IP
        # but isn't a domain we already have listed
        new_domain = str(green_ip.ip_start)

        rf = APIRequestFactory()
        url_path = reverse("green-domain-detail", kwargs={"url": new_domain})
        logger.info(f"url_path: {url_path}")

        request = rf.get(url_path)

        view = GreenDomainViewset.as_view({"get": "retrieve"})

        response = view(request, url=new_domain)

        assert response.status_code == 200
        assert response.data["green"] is True

        # do we still have the same number of green domains listed? We defer
        # persistence til later, typically outside the request/response lifecycle
        assert GreenDomain.objects.all().count() == 1


class TestGreenDomainBatchView:
    def test_check_multple_urls_via_post(
        self,
        hosting_provider_with_sample_user: ac_models.Hostingprovider,
        green_ip: GreencheckIp,
        client,
    ):
        """
        Check multiple URLs, sent as a batch request
        """
        domains = ["google.com", "anothergreendomain.com"]

        fake_csv_file = io.StringIO()
        for domain in domains:
            fake_csv_file.write(f"{domain}\n")
        fake_csv_file.seek(0)

        setup_domains(domains, hosting_provider_with_sample_user, green_ip)

        url_path = reverse("green-domain-batch")
        response = client.post(url_path, {"urls": fake_csv_file})
        returned_domains = [data.get("url") for data in response.data]

        assert response.status_code == 200
        assert len(response.data) == 2

        for domain in domains:
            assert domain in returned_domains

    def test_check_green_and_grey_urls(
        self,
        hosting_provider_with_sample_user: ac_models.Hostingprovider,
        green_ip: GreencheckIp,
        client,
    ):
        green_domains = ["google.com", "anothergreendomain.com"]
        grey_domains = ["fossilfuels4ever.com"]

        fake_csv_file = io.StringIO()
        for domain in green_domains:
            fake_csv_file.write(f"{domain}\n")

        for domain in grey_domains:
            fake_csv_file.write(f"{domain}\n")

        fake_csv_file.seek(0)

        setup_domains(green_domains, hosting_provider_with_sample_user, green_ip)

        url_path = reverse("green-domain-batch")
        response = client.post(url_path, {"urls": fake_csv_file})
        returned_domains = [data.get("url") for data in response.data]

        assert response.status_code == 200
        assert len(response.data) == 3

        domains = green_domains + grey_domains
        for domain in domains:
            assert domain in returned_domains

    def test_check_green_and_grey_urls_csv(
        self,
        hosting_provider_with_sample_user: ac_models.Hostingprovider,
        green_ip: GreencheckIp,
        client,
    ):
        green_domains = ["google.com", "anothergreendomain.com"]
        grey_domains = ["fossilfuels4ever.com"]

        fake_csv_file = io.StringIO()
        for domain in green_domains:
            fake_csv_file.write(f"{domain}\n")

        for domain in grey_domains:
            fake_csv_file.write(f"{domain}\n")

        fake_csv_file.seek(0)

        setup_domains(green_domains, hosting_provider_with_sample_user, green_ip)

        url_path = reverse("green-domain-batch")
        response = client.post(
            url_path,
            {"urls": fake_csv_file, "response_filename": "given_filename.csv"},
            HTTP_ACCEPT="text/csv",
        )

        assert response.accepted_media_type == "text/csv"
        assert response.status_code == 200

        parsed_domains = parse_csv_from_response(response)
        returned_domains = [data.get("url") for data in parsed_domains]

        assert len(returned_domains) == 3

        domains = green_domains + grey_domains
        for domain in domains:
            assert domain in returned_domains

        assert (
            response["Content-Disposition"] == "attachment; filename=given_filename.csv"
        )
