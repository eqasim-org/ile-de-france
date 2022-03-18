import pandas as pd

"""
This stage creates the various type of vehicles needed for the simulation with HBEFA emissions
"""

HBEFA_TECH = ['petrol', 'diesel']
HBEFA_EURO = ['1', '2', '3', '4', '5', '6ab', '6c', '6d']

def configure(context):
    pass

def execute(context):

    vehicle_types = [
        {
            'type_id': 'default_car', 'nb_seats': 4, 'length': 5.0, 'width': 1.0, 'pce': 1.0, 'mode': "car",
            'hbefa_cat': "PASSENGER_CAR", 'hbefa_tech': "average", 'hbefa_size': "average", 'hbefa_emission': "average",
        }
    ]

    for technology in HBEFA_TECH:
        for euro in HBEFA_EURO:
            tech = technology

            id = "car_%s_%s" % (technology, euro)

            if technology == "diesel" and euro in ['2', '3']:
                euro += " (DPF)"

            size = ">=2L" if technology == "petrol" else "<1,4L"

            if technology == "petrol":
                tech += " (4S)"

            emission = "PC %s Euro-%s" % (tech, euro)

            vehicle_types.append({
                'type_id': id, 'length': 7.5, 'width': 1.0,
                'hbefa_cat': "PASSENGER_CAR", 'hbefa_tech': tech, 'hbefa_size': size, 'hbefa_emission': emission,
            })

    df_types = pd.DataFrame.from_records(vehicle_types)
    return df_types


"""
<vehicleType id="PC petrol Euro-1">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">petrol (4S)</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&gt;=2L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC petrol Euro-1</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC petrol Euro-2">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">petrol (4S)</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&gt;=2L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC petrol Euro-2</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC petrol Euro-3">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">petrol (4S)</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&gt;=2L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC petrol Euro-3</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC petrol Euro-4">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">petrol (4S)</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&gt;=2L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC petrol Euro-4</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC petrol Euro-5">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">petrol (4S)</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&gt;=2L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC petrol Euro-5</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC petrol Euro-6ab">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">petrol (4S)</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&gt;=2L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC petrol Euro-6ab</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC petrol Euro-6c">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">petrol (4S)</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&gt;=2L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC petrol Euro-6c</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>

	<vehicleType id="PC petrol Euro-6d">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">petrol (4S)</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&gt;=2L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC petrol Euro-6d</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC diesel Euro-1">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">diesel</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&lt;1,4L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC diesel Euro-1</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC diesel Euro-2 (DPF)">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">diesel</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&lt;1,4L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC diesel Euro-2 (DPF)</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC diesel Euro-3 (DPF)">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">diesel</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&lt;1,4L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC diesel Euro-3 (DPF)</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC diesel Euro-4">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">diesel</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&lt;1,4L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC diesel Euro-4</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC diesel Euro-5">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">diesel</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&lt;1,4L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC diesel Euro-5</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC diesel Euro-6ab">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">diesel</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&lt;1,4L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC diesel Euro-6ab</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
	
	<vehicleType id="PC diesel Euro-6c">
		<length meter="7.5"/>
		<width meter="1.0"/>
		<engineInformation>
			<attributes>
				<attribute name="HbefaVehicleCategory" class="java.lang.String">PASSENGER_CAR</attribute>
				<attribute name="HbefaTechnology" class="java.lang.String">diesel</attribute>
				<attribute name="HbefaSizeClass" class="java.lang.String">&lt;1,4L</attribute>
				<attribute name="HbefaEmissionsConcept" class="java.lang.String">PC diesel Euro-6c</attribute>
			</attributes>
		</engineInformation>
	</vehicleType>
"""