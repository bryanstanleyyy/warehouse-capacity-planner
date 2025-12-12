import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  FormControlLabel,
  Checkbox,
  Box,
} from '@mui/material';
import type { Zone, ZoneInput } from '../../types/warehouse';

interface ZoneDialogProps {
  open: boolean;
  zone: Zone | null;
  onClose: () => void;
  onSubmit: (data: ZoneInput) => void;
  isLoading?: boolean;
}

export default function ZoneDialog({
  open,
  zone,
  onClose,
  onSubmit,
  isLoading = false,
}: ZoneDialogProps) {
  const [formData, setFormData] = useState<ZoneInput>({
    name: '',
    zone_order: 0,
    area: 0,
    height: 0,
    strength: undefined,
    climate_controlled: false,
    temperature_min: undefined,
    temperature_max: undefined,
    special_handling: false,
    container_capacity: 0,
    is_weather_zone: false,
  });

  useEffect(() => {
    if (zone) {
      setFormData({
        name: zone.name,
        zone_order: zone.zone_order || 0,
        area: zone.area,
        height: zone.height,
        strength: zone.strength,
        climate_controlled: zone.climate_controlled || false,
        temperature_min: zone.temperature_min,
        temperature_max: zone.temperature_max,
        special_handling: zone.special_handling || false,
        container_capacity: zone.container_capacity || 0,
        is_weather_zone: zone.is_weather_zone || false,
      });
    } else {
      resetForm();
    }
  }, [zone, open]);

  const resetForm = () => {
    setFormData({
      name: '',
      zone_order: 0,
      area: 0,
      height: 0,
      strength: undefined,
      climate_controlled: false,
      temperature_min: undefined,
      temperature_max: undefined,
      special_handling: false,
      container_capacity: 0,
      is_weather_zone: false,
    });
  };

  const handleSubmit = () => {
    onSubmit(formData);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>{zone ? 'Edit Zone' : 'Add Zone'}</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={8}>
              <TextField
                label="Zone Name"
                fullWidth
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Zone A, Ground Floor, Upper Deck"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Display Order"
                type="number"
                fullWidth
                value={formData.zone_order}
                onChange={(e) =>
                  setFormData({ ...formData, zone_order: parseInt(e.target.value) || 0 })
                }
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ fontWeight: 'medium', mb: 1, color: 'text.secondary' }}>
                Capacity Specifications
              </Box>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                label="Area (sq ft)"
                type="number"
                fullWidth
                required
                value={formData.area}
                onChange={(e) =>
                  setFormData({ ...formData, area: parseFloat(e.target.value) || 0 })
                }
                inputProps={{ min: 0, step: 0.01 }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Height (ft)"
                type="number"
                fullWidth
                required
                value={formData.height}
                onChange={(e) =>
                  setFormData({ ...formData, height: parseFloat(e.target.value) || 0 })
                }
                inputProps={{ min: 0, step: 0.01 }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Floor Strength (PSF)"
                type="number"
                fullWidth
                value={formData.strength || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    strength: e.target.value ? parseFloat(e.target.value) : undefined,
                  })
                }
                placeholder="Optional"
                inputProps={{ min: 0, step: 1 }}
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ fontWeight: 'medium', mb: 1, mt: 1, color: 'text.secondary' }}>
                Zone Capabilities
              </Box>
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.climate_controlled}
                    onChange={(e) =>
                      setFormData({ ...formData, climate_controlled: e.target.checked })
                    }
                  />
                }
                label="Climate Controlled"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.special_handling}
                    onChange={(e) =>
                      setFormData({ ...formData, special_handling: e.target.checked })
                    }
                  />
                }
                label="Special Handling"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.is_weather_zone}
                    onChange={(e) =>
                      setFormData({ ...formData, is_weather_zone: e.target.checked })
                    }
                  />
                }
                label="Outdoor Storage Zone"
              />
            </Grid>

            {formData.climate_controlled && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Min Temperature (°F)"
                    type="number"
                    fullWidth
                    value={formData.temperature_min || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        temperature_min: e.target.value ? parseFloat(e.target.value) : undefined,
                      })
                    }
                    inputProps={{ step: 1 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Max Temperature (°F)"
                    type="number"
                    fullWidth
                    value={formData.temperature_max || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        temperature_max: e.target.value ? parseFloat(e.target.value) : undefined,
                      })
                    }
                    inputProps={{ step: 1 }}
                  />
                </Grid>
              </>
            )}

            <Grid item xs={12} sm={6}>
              <TextField
                label="Container Capacity"
                type="number"
                fullWidth
                value={formData.container_capacity}
                onChange={(e) =>
                  setFormData({ ...formData, container_capacity: parseInt(e.target.value) || 0 })
                }
                inputProps={{ min: 0, step: 1 }}
              />
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={!formData.name || !formData.area || !formData.height || isLoading}
        >
          {zone ? 'Update' : 'Add'} Zone
        </Button>
      </DialogActions>
    </Dialog>
  );
}
