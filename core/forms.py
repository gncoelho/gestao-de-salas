import json
from django import forms
from .models import Sala

DAYS_OF_WEEK = [
    ('monday', 'Monday (Segunda-feira)'),
    ('tuesday', 'Tuesday (Terça-feira)'),
    ('wednesday', 'Wednesday (Quarta-feira)'),
    ('thursday', 'Thursday (Quinta-feira)'),
    ('friday', 'Friday (Sexta-feira)'),
    ('saturday', 'Saturday (Sábado)'),
    ('sunday', 'Sunday (Domingo)'),
]

class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for day_code, day_label in DAYS_OF_WEEK:
            self.fields[f'{day_code}_from'] = forms.IntegerField(
                required=False,
                label=f'{day_label} - From (De)',
                min_value=0,
                max_value=23,
                widget=forms.NumberInput(attrs={'placeholder': 'e.g. 9', 'class': 'form-control'})
            )
            self.fields[f'{day_code}_to'] = forms.IntegerField(
                required=False,
                label=f'{day_label} - To (Até)',
                min_value=0,
                max_value=24,
                widget=forms.NumberInput(attrs={'placeholder': 'e.g. 17', 'class': 'form-control'})
            )
            self.fields[f'{day_code}_json'] = forms.CharField(
                required=False,
                widget=forms.HiddenInput(),
                help_text="Optional raw JSON string for advanced multiple slots"
            )

            # If instance exists, populate initial values
            if self.instance and self.instance.pk and self.instance.horarios_disponiveis:
                slots = self.instance.horarios_disponiveis.get(day_code, [])
                if slots and isinstance(slots, list) and len(slots) > 0:
                    first_slot = slots[0]
                    if isinstance(first_slot, dict):
                        self.fields[f'{day_code}_from'].initial = first_slot.get('from')
                        self.fields[f'{day_code}_to'].initial = first_slot.get('to')

    def clean(self):
        cleaned_data = super().clean()
        horarios = {}

        for day_code, _ in DAYS_OF_WEEK:
            from_val = cleaned_data.get(f'{day_code}_from')
            to_val = cleaned_data.get(f'{day_code}_to')
            json_val = cleaned_data.get(f'{day_code}_json')

            day_slots = []
            if json_val:
                try:
                    parsed = json.loads(json_val)
                    if isinstance(parsed, list):
                        for slot in parsed:
                            if isinstance(slot, dict) and 'from' in slot and 'to' in slot:
                                day_slots.append({
                                    'from': int(slot['from']),
                                    'to': int(slot['to'])
                                })
                except Exception:
                    pass

            if not day_slots:
                if from_val is not None and to_val is not None:
                    if from_val >= to_val:
                        self.add_error(f'{day_code}_to', f"'{day_code}' end hour ('to') must be greater than start hour ('from').")
                    else:
                        day_slots.append({
                            'from': int(from_val),
                            'to': int(to_val)
                        })
                elif from_val is not None and to_val is None:
                    self.add_error(f'{day_code}_to', f"Please enter 'to' hour for {day_code}.")
                elif from_val is None and to_val is not None:
                    self.add_error(f'{day_code}_from', f"Please enter 'from' hour for {day_code}.")

            if day_slots:
                horarios[day_code] = day_slots

        cleaned_data['horarios_disponiveis'] = horarios
        return cleaned_data

    def save(self, commit=True):
        sala = super().save(commit=False)
        sala.horarios_disponiveis = self.cleaned_data.get('horarios_disponiveis', {})
        if commit:
            sala.save()
        return sala
