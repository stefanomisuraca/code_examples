def send_csv_email(custom_root="/util/csv/", delimiter=","):
    EMAIL_TITLE = "Some Title"  # noqa
    EMAIL_SENDER = settings.EMAIL
    stop_attachments = False

    csv_name = input("Enter csv path: \n")
    assert isinstance(csv_name, str), "csv name paramater is not a string"
    csv_path = f"{custom_root}{csv_name}"

    template_name = input("Enter template name: \n")
    assert isinstance(template_name, str), "template name paramater is not a string"  # noqa

    attachments = []
    while True:
        attachment = input("Select attachment: \n")
        if str(attachment).lower() == "stop" or str(attachment).lower() == "":
            break
        attachments.append(f"{custom_root}{attachment}")

    try:
        with open(csv_path, "r+") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=delimiter)
            line_count = 0
            for row in csv_reader:
                first_name = row.get('First Name')
                last_name = row.get('Last Name')
                company = row.get('Company')
                title = row.get('Title')
                email = row.get('Email')
                phone = row.get('Phone')
                params = {
                    "first_name": first_name,
                    "last_name": last_name
                }
                send_email_external(
                    template_name, EMAIL_TITLE, email,
                    additional_params=params,
                    files=attachments,
                    sender=EMAIL_SENDER
                )
                print(f"email sent to: {email}")
                line_count += 1
            print(f'Processed {line_count} lines.')
    except FileNotFoundError:
        return {"error": "File not found"}
    return


def pt_clients_csv_data(user_id_list: list):
    """Return clients' data in csv format."""

    return_fields = [
        "date_taken", "user", "weight",
        "height", "chest", "waist", "hips",
        "body_fat", "thigh_left", "thigh_right", "calf_left",
        "calf_right", "biceps_left", "biceps_right", "volume_body"
    ]

    def normalize_value(val):
        if isinstance(val, datetime):
            return val.strftime("%Y-%m-%d, %H:%M:%S")
        elif isinstance(val, User):
            return hashlib.sha256(str(val.id).encode('utf-8')).hexdigest()[:10]
        else:
            return str(val)

    list_to_csv = []
    for user in user_id_list:
        scans = Scan.objects.filter(
            status="complete",
            user_id=user
        )
        list_to_csv += list(
            map(
                lambda scan: [normalize_value(getattr(scan, field)) for field in return_fields],  # noqa
                scans
            )
        )
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(return_fields)
    writer.writerows(list_to_csv)
    return output.getvalue().strip("\r\n")
