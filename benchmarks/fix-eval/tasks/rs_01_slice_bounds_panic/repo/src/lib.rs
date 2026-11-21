pub fn moving_average(values: &[f64], window: usize) -> Vec<f64> {
    let mut out = Vec::new();
    for i in 0..=(values.len() - window) {
        let sum: f64 = values[i..i + window].iter().sum();
        out.push(sum / window as f64);
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn handles_normal_window() {
        assert_eq!(moving_average(&[2.0, 4.0, 6.0, 8.0], 2), vec![3.0, 5.0, 7.0]);
    }

    #[test]
    fn handles_empty_or_oversized_window() {
        assert_eq!(moving_average(&[], 3), Vec::<f64>::new());
        assert_eq!(moving_average(&[1.0, 2.0], 5), Vec::<f64>::new());
        assert_eq!(moving_average(&[1.0, 2.0], 0), Vec::<f64>::new());
    }
}
