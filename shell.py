def main():
    from gevent.monkey import patch_all
    patch_all(subprocess=True)

    import sys
    import os

    code_dir = os.path.dirname(os.path.abspath(sys.path[0]))


    # Make sure egg-info files are on the PYTHONPATH
    sys.path.append(code_dir)


    # Requests bundles cacert.pem, but it can't see it inside library.zip
    # The bundler will ship cacert.pem alongside yaybu.exe
    import requests.certs
    requests.certs.where = lambda: os.path.join(code_dir, "cacert.pem")


    # libcloud depends on a system cert bundle. Point it at the requests
    # cacert.pem...
    import libcloud.security
    libcloud.security.CA_CERTS_PATH.append(
        os.path.join(code_dir, "cacert.pem")
        )


    # Make sure the yay generated files are included in the bundle
    from yay import lextab
    from yay import parsetab


    from yaybu.core.main import main
    main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
