"use client"
// Using Autocomplete from Material UI
// Documentation here: https://mui.com/material-ui/react-autocomplete/

import TextField from "@mui/material/TextField"
import Autocomplete from "@mui/material/Autocomplete"

interface Props {
	items: { Label: string; id: number }[]
	onSelectItem: (item: number | -1) => void
	dropdownLabel: string
	isDisabled: boolean
}

export default function Dropdown({
	items,
	onSelectItem,
	dropdownLabel,
	isDisabled,
}: Props) {
	if (isDisabled) {
		return (
			<Autocomplete
				disablePortal
				disabled
				//input data stuff below
				options={items}
				getOptionLabel={(items) => items.Label}
				sx={{ width: 300 }}
				onChange={(a, b) => {
					onSelectItem(b!.id)
				}}
				renderInput={(params) => (
					<TextField {...params} label={dropdownLabel} color="primary" />
				)}
			/>
		)
	}
	return (
		<Autocomplete
			disablePortal
			//input data stuff below
			options={items}
			getOptionLabel={(items) => items.Label}
			sx={{ width: 300 }}
			onChange={(a, b) => {
				if (b != null) {
					onSelectItem(b!.id)
				} else {
					onSelectItem(-1)
				}
			}}
			renderInput={(params) => (
				<TextField {...params} label={dropdownLabel} color="primary" />
			)}
		/>
	)
}
