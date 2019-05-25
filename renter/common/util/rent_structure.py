from datetime import datetime, timedelta


#Goes through all the available data, removes inactive charges,
#marks late charges,
def calculate_rent_structure(charges):
    one_time_charges = []
    recurring_charges = []
    todays_date = datetime.now().date()
    for charge in charges:
        if charge.paid:
            continue

        if charge.due_date < todays_date:
            charge.alert = 'danger'
            charge.status = 'late'
        elif charge.due_date > (todays_date + timedelta(days=7)):
            charge.alert = 'info'
            charge.status = 'upcoming'
        else:
            charge.alert = 'warning'
            charge.status = 'due soon'

        if charge.recurring:
            if charge.recurring_until < todays_date:
                pass
            else:
                recurring_charges.append(charge)
        else:
            one_time_charges.append(charge)
        charge.save()

    return {
        'one_time_charges': one_time_charges,
        'recurring_charges': recurring_charges
    }
